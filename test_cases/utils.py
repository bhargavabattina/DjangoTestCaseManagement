import openpyxl
import pandas as pd
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import TestCase, UserStory
import logging

logger = logging.getLogger(__name__)


def validate_excel_headers(worksheet):
    """
    Validate that the Excel file has the required headers.
    Expected headers: Test Case Name, Description, Test Steps, Expected Results, Priority, Is Automated
    """
    required_headers = [
        'Test Case Name',
        'Description', 
        'Test Steps',
        'Expected Results',
        'Priority',
        'Is Automated'
    ]
    
    # Get first row (headers)
    headers = []
    for cell in worksheet[1]:
        if cell.value:
            headers.append(str(cell.value).strip())
    
    missing_headers = []
    for required_header in required_headers:
        if required_header not in headers:
            missing_headers.append(required_header)
    
    if missing_headers:
        return False, f"Missing required headers: {', '.join(missing_headers)}"
    
    return True, headers


def validate_testcase_data(row_data, row_number):
    """
    Validate individual test case data from Excel row.
    Returns tuple (is_valid, errors_list)
    """
    errors = []
    
    # Check required fields
    if not row_data.get('Test Case Name', '').strip():
        errors.append(f"Row {row_number}: Test Case Name is required")
    elif len(row_data.get('Test Case Name', '').strip()) < 5:
        errors.append(f"Row {row_number}: Test Case Name must be at least 5 characters long")
    
    if not row_data.get('Test Steps', '').strip():
        errors.append(f"Row {row_number}: Test Steps are required")
    elif len(row_data.get('Test Steps', '').strip()) < 10:
        errors.append(f"Row {row_number}: Test Steps must be at least 10 characters long")
    
    if not row_data.get('Expected Results', '').strip():
        errors.append(f"Row {row_number}: Expected Results are required")
    elif len(row_data.get('Expected Results', '').strip()) < 10:
        errors.append(f"Row {row_number}: Expected Results must be at least 10 characters long")
    
    # Validate priority
    valid_priorities = ['low', 'medium', 'high', 'critical']
    priority = str(row_data.get('Priority', 'medium')).lower().strip()
    if priority and priority not in valid_priorities:
        errors.append(f"Row {row_number}: Priority must be one of: {', '.join(valid_priorities)}")
    
    # Validate is_automated
    is_automated_value = str(row_data.get('Is Automated', 'False')).lower().strip()
    if is_automated_value not in ['true', 'false', '1', '0', 'yes', 'no']:
        errors.append(f"Row {row_number}: Is Automated must be True/False, Yes/No, or 1/0")
    
    return len(errors) == 0, errors


def parse_excel_file(excel_file):
    """
    Parse Excel file and return list of test case data dictionaries.
    Returns tuple (success, data_list, error_message)
    """
    try:
        # Try to read with openpyxl first
        workbook = openpyxl.load_workbook(excel_file, data_only=True)
        worksheet = workbook.active
        
        # Validate headers
        headers_valid, headers_or_error = validate_excel_headers(worksheet)
        if not headers_valid:
            return False, [], headers_or_error
        
        headers = headers_or_error
        
        # Parse data rows
        data_list = []
        errors = []
        
        for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
            if not any(row):  # Skip empty rows
                continue
            
            # Create dictionary from row data
            row_data = {}
            for col_idx, header in enumerate(headers):
                if col_idx < len(row):
                    cell_value = row[col_idx]
                    row_data[header] = str(cell_value) if cell_value is not None else ''
                else:
                    row_data[header] = ''
            
            # Validate row data
            is_valid, validation_errors = validate_testcase_data(row_data, row_idx)
            if is_valid:
                data_list.append(row_data)
            else:
                errors.extend(validation_errors)
        
        if errors:
            return False, [], f"Validation errors found:\n" + "\n".join(errors)
        
        return True, data_list, ""
        
    except Exception as e:
        logger.error(f"Error parsing Excel file: {str(e)}")
        return False, [], f"Error reading Excel file: {str(e)}"


def convert_boolean_value(value):
    """
    Convert various boolean representations to Python boolean.
    """
    if isinstance(value, bool):
        return value
    
    value_str = str(value).lower().strip()
    return value_str in ['true', '1', 'yes', 'y']


def normalize_priority(priority_value):
    """
    Normalize priority value to valid choice.
    """
    priority_str = str(priority_value).lower().strip()
    priority_mapping = {
        'low': 'low',
        'l': 'low',
        'medium': 'medium',
        'med': 'medium',
        'm': 'medium',
        'high': 'high',
        'h': 'high',
        'critical': 'critical',
        'crit': 'critical',
        'c': 'critical'
    }
    
    return priority_mapping.get(priority_str, 'medium')


def create_testcase_from_data(testcase_data, user_story, created_by):
    """
    Create a TestCase instance from parsed Excel data.
    Returns tuple (testcase_instance, success, error_message)
    """
    try:
        # Normalize data
        name = testcase_data.get('Test Case Name', '').strip()
        description = testcase_data.get('Description', '').strip()
        test_steps = testcase_data.get('Test Steps', '').strip()
        expected_results = testcase_data.get('Expected Results', '').strip()
        priority = normalize_priority(testcase_data.get('Priority', 'medium'))
        is_automated = convert_boolean_value(testcase_data.get('Is Automated', 'False'))
        
        # Create TestCase instance
        testcase = TestCase(
            name=name,
            description=description,
            test_steps=test_steps,
            expected_results=expected_results,
            priority=priority,
            is_automated=is_automated,
            user_story=user_story,
            created_by=created_by,
            status='draft',
            execution_status='not_executed'
        )
        
        # Validate the instance
        testcase.full_clean()
        
        return testcase, True, ""
        
    except ValidationError as e:
        error_msg = "; ".join([f"{field}: {', '.join(errors)}" for field, errors in e.message_dict.items()])
        return None, False, f"Validation error: {error_msg}"
    except Exception as e:
        return None, False, f"Error creating test case: {str(e)}"


@transaction.atomic
def import_testcases_from_excel(excel_file, user_story, created_by):
    """
    Main function to import test cases from Excel file.
    Returns dictionary with results: {
        'success': bool,
        'created': int,
        'errors': list,
        'error': str (if success is False)
    }
    """
    result = {
        'success': False,
        'created': 0,
        'errors': [],
        'error': ''
    }
    
    try:
        # Validate user_story exists and user has permission
        if not isinstance(user_story, UserStory):
            result['error'] = "Invalid user story provided"
            return result
        
        # Check if user has permission to create test cases for this user story
        if user_story.epic.project.created_by != created_by:
            result['error'] = "You don't have permission to create test cases for this user story"
            return result
        
        # Parse Excel file
        parse_success, testcase_data_list, parse_error = parse_excel_file(excel_file)
        if not parse_success:
            result['error'] = parse_error
            return result
        
        if not testcase_data_list:
            result['error'] = "No valid test case data found in Excel file"
            return result
        
        # Create test cases
        created_testcases = []
        errors = []
        
        for idx, testcase_data in enumerate(testcase_data_list, start=1):
            testcase, create_success, create_error = create_testcase_from_data(
                testcase_data, user_story, created_by
            )
            
            if create_success:
                created_testcases.append(testcase)
            else:
                errors.append(f"Row {idx + 1}: {create_error}")
        
        # Bulk create test cases if any were successfully prepared
        if created_testcases:
            try:
                TestCase.objects.bulk_create(created_testcases)
                result['created'] = len(created_testcases)
                logger.info(f"Successfully imported {len(created_testcases)} test cases for user {created_by.username}")
            except Exception as e:
                result['error'] = f"Error saving test cases to database: {str(e)}"
                return result
        
        result['success'] = True
        result['errors'] = errors
        
        # Log summary
        if errors:
            logger.warning(f"Import completed with {len(errors)} errors for user {created_by.username}")
        
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error during Excel import: {str(e)}")
        result['error'] = f"Unexpected error during import: {str(e)}"
        return result


def generate_sample_excel_data():
    """
    Generate sample data for Excel template download.
    Returns list of dictionaries representing sample test cases.
    """
    sample_data = [
        {
            'Test Case Name': 'Login with valid credentials',
            'Description': 'Test successful login with valid username and password',
            'Test Steps': '1. Navigate to login page\n2. Enter valid username\n3. Enter valid password\n4. Click login button',
            'Expected Results': 'User should be successfully logged in and redirected to dashboard',
            'Priority': 'high',
            'Is Automated': 'False'
        },
        {
            'Test Case Name': 'Login with invalid credentials',
            'Description': 'Test login failure with invalid credentials',
            'Test Steps': '1. Navigate to login page\n2. Enter invalid username\n3. Enter invalid password\n4. Click login button',
            'Expected Results': 'Error message should be displayed and user should remain on login page',
            'Priority': 'medium',
            'Is Automated': 'True'
        },
        {
            'Test Case Name': 'Password reset functionality',
            'Description': 'Test password reset feature',
            'Test Steps': '1. Click forgot password link\n2. Enter email address\n3. Click submit\n4. Check email for reset link',
            'Expected Results': 'Password reset email should be sent with valid reset link',
            'Priority': 'low',
            'Is Automated': 'False'
        }
    ]
    
    return sample_data


def export_testcases_to_excel(testcases, filename=None):
    """
    Export test cases to Excel format.
    Returns tuple (success, file_path_or_error_message)
    """
    try:
        import io
        from django.http import HttpResponse
        
        # Create workbook and worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Test Cases"
        
        # Define headers
        headers = [
            'Test Case Name', 'Description', 'Test Steps', 'Expected Results',
            'Priority', 'Status', 'Execution Status', 'Is Automated',
            'User Story', 'Epic', 'Project', 'Created Date', 'Updated Date'
        ]
        
        # Write headers
        for col_idx, header in enumerate(headers, start=1):
            worksheet.cell(row=1, column=col_idx, value=header)
        
        # Write test case data
        for row_idx, testcase in enumerate(testcases, start=2):
            worksheet.cell(row=row_idx, column=1, value=testcase.name)
            worksheet.cell(row=row_idx, column=2, value=testcase.description)
            worksheet.cell(row=row_idx, column=3, value=testcase.test_steps)
            worksheet.cell(row=row_idx, column=4, value=testcase.expected_results)
            worksheet.cell(row=row_idx, column=5, value=testcase.get_priority_display())
            worksheet.cell(row=row_idx, column=6, value=testcase.get_status_display())
            worksheet.cell(row=row_idx, column=7, value=testcase.get_execution_status_display())
            worksheet.cell(row=row_idx, column=8, value='Yes' if testcase.is_automated else 'No')
            worksheet.cell(row=row_idx, column=9, value=testcase.user_story.name)
            worksheet.cell(row=row_idx, column=10, value=testcase.user_story.epic.name)
            worksheet.cell(row=row_idx, column=11, value=testcase.user_story.epic.project.name)
            worksheet.cell(row=row_idx, column=12, value=testcase.created_date.strftime('%Y-%m-%d %H:%M:%S'))
            worksheet.cell(row=row_idx, column=13, value=testcase.updated_date.strftime('%Y-%m-%d %H:%M:%S'))
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Save to BytesIO if no filename provided (for HTTP response)
        if not filename:
            excel_buffer = io.BytesIO()
            workbook.save(excel_buffer)
            excel_buffer.seek(0)
            return True, excel_buffer
        else:
            workbook.save(filename)
            return True, filename
            
    except Exception as e:
        logger.error(f"Error exporting test cases to Excel: {str(e)}")
        return False, f"Error exporting to Excel: {str(e)}"
