from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import Avg, Sum
from datetime import datetime, timedelta
import json
from .models import Project, Epic, UserStory, TestCase, TestRun, TestExecution, TestExecutionStep, TestSuite
from .forms import (
    ProjectForm, EpicForm, UserStoryForm, TestCaseForm, 
    ExcelUploadForm, UserRegistrationForm, UserLoginForm,
    TestRunForm, TestExecutionForm, TestExecutionStepForm, TestSuiteForm,
    TestExecutionReportForm, BulkTestExecutionForm
)


def user_register(request):
    if request.user.is_authenticated:
        return redirect('test_cases:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add user to default group if needed
            try:
                default_group, created = Group.objects.get_or_create(name='Test_Users')
                user.groups.add(default_group)
            except:
                pass
            
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('test_cases:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('test_cases:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'test_cases:dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'registration/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('test_cases:login')


@login_required
def dashboard(request):
    # Get statistics
    projects_count = Project.objects.filter(created_by=request.user).count()
    epics_count = Epic.objects.filter(project__created_by=request.user).count()
    stories_count = UserStory.objects.filter(epic__project__created_by=request.user).count()
    testcases_count = TestCase.objects.filter(user_story__epic__project__created_by=request.user).count()
    
    # Get recent activities
    recent_projects = Project.objects.filter(created_by=request.user)[:5]
    recent_testcases = TestCase.objects.filter(user_story__epic__project__created_by=request.user)[:5]
    
    context = {
        'projects_count': projects_count,
        'epics_count': epics_count,
        'stories_count': stories_count,
        'testcases_count': testcases_count,
        'recent_projects': recent_projects,
        'recent_testcases': recent_testcases,
    }
    
    return render(request, 'dashboard.html', context)


# Project Views
@login_required
def project_list(request):
    projects = Project.objects.filter(created_by=request.user).order_by('-created_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    
    context = {
        'projects': projects,
        'search_query': search_query,
    }
    return render(request, 'projects/list.html', context)


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('test_cases:project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'projects/form.html', {
        'form': form,
        'title': 'Create Project',
        'action': 'Create'
    })


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('test_cases:project_list')
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/form.html', {
        'form': form,
        'title': 'Edit Project',
        'action': 'Update',
        'project': project
    })


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" deleted successfully!')
        return redirect('test_cases:project_list')
    
    return render(request, 'projects/confirm_delete.html', {'project': project})


# Epic Views
@login_required
def epic_list(request):
    epics = Epic.objects.filter(project__created_by=request.user).order_by('-created_date')
    
    # Filter by project
    project_id = request.GET.get('project')
    if project_id:
        epics = epics.filter(project_id=project_id)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        epics = epics.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(project__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(epics, 10)
    page_number = request.GET.get('page')
    epics = paginator.get_page(page_number)
    
    # Get projects for filter dropdown
    projects = Project.objects.filter(created_by=request.user)
    
    context = {
        'epics': epics,
        'projects': projects,
        'selected_project': project_id,
        'search_query': search_query,
    }
    return render(request, 'epics/list.html', context)


@login_required
def epic_create(request):
    if request.method == 'POST':
        form = EpicForm(request.POST, user=request.user)
        if form.is_valid():
            epic = form.save(commit=False)
            epic.created_by = request.user
            epic.save()
            messages.success(request, 'Epic created successfully!')
            return redirect('test_cases:epic_list')
    else:
        form = EpicForm(user=request.user)
    
    return render(request, 'epics/form.html', {
        'form': form,
        'title': 'Create Epic',
        'action': 'Create'
    })


@login_required
def epic_edit(request, pk):
    epic = get_object_or_404(Epic, pk=pk, project__created_by=request.user)
    
    if request.method == 'POST':
        form = EpicForm(request.POST, instance=epic, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Epic updated successfully!')
            return redirect('test_cases:epic_list')
    else:
        form = EpicForm(instance=epic, user=request.user)
    
    return render(request, 'epics/form.html', {
        'form': form,
        'title': 'Edit Epic',
        'action': 'Update',
        'epic': epic
    })


@login_required
def epic_delete(request, pk):
    epic = get_object_or_404(Epic, pk=pk, project__created_by=request.user)
    
    if request.method == 'POST':
        epic_name = epic.name
        epic.delete()
        messages.success(request, f'Epic "{epic_name}" deleted successfully!')
        return redirect('test_cases:epic_list')
    
    return render(request, 'epics/confirm_delete.html', {'epic': epic})


# UserStory Views
@login_required
def story_list(request):
    stories = UserStory.objects.filter(epic__project__created_by=request.user).order_by('-created_date')
    
    # Filter by project and epic
    project_id = request.GET.get('project')
    epic_id = request.GET.get('epic')
    
    if project_id:
        stories = stories.filter(epic__project_id=project_id)
    if epic_id:
        stories = stories.filter(epic_id=epic_id)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        stories = stories.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(epic__name__icontains=search_query) |
            Q(epic__project__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(stories, 10)
    page_number = request.GET.get('page')
    stories = paginator.get_page(page_number)
    
    # Get projects and epics for filter dropdowns
    projects = Project.objects.filter(created_by=request.user)
    epics = Epic.objects.filter(project__created_by=request.user)
    
    context = {
        'stories': stories,
        'projects': projects,
        'epics': epics,
        'selected_project': project_id,
        'selected_epic': epic_id,
        'search_query': search_query,
    }
    return render(request, 'stories/list.html', context)


@login_required
def story_create(request):
    if request.method == 'POST':
        form = UserStoryForm(request.POST, user=request.user)
        if form.is_valid():
            story = form.save(commit=False)
            story.created_by = request.user
            story.save()
            messages.success(request, 'User Story created successfully!')
            return redirect('test_cases:story_list')
    else:
        form = UserStoryForm(user=request.user)
    
    return render(request, 'stories/form.html', {
        'form': form,
        'title': 'Create User Story',
        'action': 'Create'
    })


@login_required
def story_edit(request, pk):
    story = get_object_or_404(UserStory, pk=pk, epic__project__created_by=request.user)
    
    if request.method == 'POST':
        form = UserStoryForm(request.POST, instance=story, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User Story updated successfully!')
            return redirect('test_cases:story_list')
    else:
        form = UserStoryForm(instance=story, user=request.user)
    
    return render(request, 'stories/form.html', {
        'form': form,
        'title': 'Edit User Story',
        'action': 'Update',
        'story': story
    })


@login_required
def story_delete(request, pk):
    story = get_object_or_404(UserStory, pk=pk, epic__project__created_by=request.user)
    
    if request.method == 'POST':
        story_name = story.name
        story.delete()
        messages.success(request, f'User Story "{story_name}" deleted successfully!')
        return redirect('test_cases:story_list')
    
    return render(request, 'stories/confirm_delete.html', {'story': story})


# TestCase Views
@login_required
def testcase_list(request):
    testcases = TestCase.objects.filter(user_story__epic__project__created_by=request.user).order_by('-created_date')
    
    # Filter by project, epic, and story
    project_id = request.GET.get('project')
    epic_id = request.GET.get('epic')
    story_id = request.GET.get('story')
    
    if project_id:
        testcases = testcases.filter(user_story__epic__project_id=project_id)
    if epic_id:
        testcases = testcases.filter(user_story__epic_id=epic_id)
    if story_id:
        testcases = testcases.filter(user_story_id=story_id)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        testcases = testcases.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(user_story__name__icontains=search_query) |
            Q(user_story__epic__name__icontains=search_query) |
            Q(user_story__epic__project__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(testcases, 15)
    page_number = request.GET.get('page')
    testcases = paginator.get_page(page_number)
    
    # Get filter options
    projects = Project.objects.filter(created_by=request.user)
    epics = Epic.objects.filter(project__created_by=request.user)
    stories = UserStory.objects.filter(epic__project__created_by=request.user)
    
    context = {
        'testcases': testcases,
        'projects': projects,
        'epics': epics,
        'stories': stories,
        'selected_project': project_id,
        'selected_epic': epic_id,
        'selected_story': story_id,
        'search_query': search_query,
    }
    return render(request, 'testcases/list.html', context)


@login_required
def testcase_create(request):
    if request.method == 'POST':
        form = TestCaseForm(request.POST, user=request.user)
        if form.is_valid():
            testcase = form.save(commit=False)
            testcase.created_by = request.user
            testcase.save()
            messages.success(request, 'Test Case created successfully!')
            return redirect('test_cases:testcase_list')
    else:
        form = TestCaseForm(user=request.user)
    
    return render(request, 'testcases/form.html', {
        'form': form,
        'title': 'Create Test Case',
        'action': 'Create'
    })


@login_required
def testcase_edit(request, pk):
    testcase = get_object_or_404(TestCase, pk=pk, user_story__epic__project__created_by=request.user)
    
    if request.method == 'POST':
        form = TestCaseForm(request.POST, instance=testcase, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test Case updated successfully!')
            return redirect('test_cases:testcase_list')
    else:
        form = TestCaseForm(instance=testcase, user=request.user)
    
    return render(request, 'testcases/form.html', {
        'form': form,
        'title': 'Edit Test Case',
        'action': 'Update',
        'testcase': testcase
    })


@login_required
def testcase_delete(request, pk):
    testcase = get_object_or_404(TestCase, pk=pk, user_story__epic__project__created_by=request.user)
    
    if request.method == 'POST':
        testcase_name = testcase.name
        testcase.delete()
        messages.success(request, f'Test Case "{testcase_name}" deleted successfully!')
        return redirect('test_cases:testcase_list')
    
    return render(request, 'testcases/confirm_delete.html', {'testcase': testcase})


@login_required
def testcase_execute(request, pk):
    testcase = get_object_or_404(TestCase, pk=pk, user_story__epic__project__created_by=request.user)
    
    if request.method == 'POST':
        execution_status = request.POST.get('execution_status')
        if execution_status in ['passed', 'failed', 'skipped']:
            testcase.execution_status = execution_status
            testcase.last_executed = timezone.now()
            testcase.save()
            messages.success(request, f'Test Case marked as {execution_status}!')
        else:
            messages.error(request, 'Invalid execution status!')
    
    return redirect('test_cases:testcase_list')


# Excel Import Views
@login_required
def testcase_import(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                from .utils import import_testcases_from_excel
                excel_file = request.FILES['excel_file']
                user_story = form.cleaned_data['user_story']
                
                result = import_testcases_from_excel(excel_file, user_story, request.user)
                
                if result['success']:
                    messages.success(request, f"Successfully imported {result['created']} test cases!")
                    if result['errors']:
                        messages.warning(request, f"Skipped {len(result['errors'])} rows due to errors.")
                else:
                    messages.error(request, f"Import failed: {result['error']}")
                    
            except ImportError:
                messages.error(request, "Excel import functionality is not available. Please check utils module.")
            except Exception as e:
                messages.error(request, f"An error occurred during import: {str(e)}")
                
            return redirect('test_cases:testcase_list')
    else:
        form = ExcelUploadForm(user=request.user)
    
    return render(request, 'testcases/import.html', {'form': form})


# AJAX Views for dynamic dropdowns
@login_required
def get_epics_by_project(request):
    project_id = request.GET.get('project_id')
    epics = Epic.objects.filter(project_id=project_id, project__created_by=request.user)
    data = [{'id': epic.id, 'name': epic.name} for epic in epics]
    return JsonResponse(data, safe=False)


@login_required
def get_stories_by_epic(request):
    epic_id = request.GET.get('epic_id')
    stories = UserStory.objects.filter(epic_id=epic_id, epic__project__created_by=request.user)
    data = [{'id': story.id, 'name': story.name} for story in stories]
    return JsonResponse(data, safe=False)


# Test Run Views
@login_required
def test_run_list(request):
    test_runs = TestRun.objects.filter(created_by=request.user).order_by('-created_date')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        test_runs = test_runs.filter(status=status)
    
    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        test_runs = test_runs.filter(created_date__gte=date_from)
    if date_to:
        test_runs = test_runs.filter(created_date__lte=date_to)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        test_runs = test_runs.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(test_runs, 10)
    page_number = request.GET.get('page')
    test_runs = paginator.get_page(page_number)
    
    context = {
        'test_runs': test_runs,
        'search_query': search_query,
        'selected_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': TestRun.STATUS_CHOICES,
    }
    return render(request, 'test_runs/list.html', context)


@login_required
def test_run_create(request):
    if request.method == 'POST':
        form = TestRunForm(request.POST)
        if form.is_valid():
            test_run = form.save(commit=False)
            test_run.created_by = request.user
            test_run.save()
            messages.success(request, 'Test Run created successfully!')
            return redirect('test_cases:test_run_list')
    else:
        form = TestRunForm()
    
    return render(request, 'test_runs/form.html', {
        'form': form,
        'title': 'Create Test Run',
        'action': 'Create'
    })


@login_required
def test_run_edit(request, pk):
    test_run = get_object_or_404(TestRun, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = TestRunForm(request.POST, instance=test_run)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test Run updated successfully!')
            return redirect('test_cases:test_run_list')
    else:
        form = TestRunForm(instance=test_run)
    
    return render(request, 'test_runs/form.html', {
        'form': form,
        'title': 'Edit Test Run',
        'action': 'Update',
        'test_run': test_run
    })


@login_required
def test_run_delete(request, pk):
    test_run = get_object_or_404(TestRun, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        test_run_name = test_run.name
        test_run.delete()
        messages.success(request, f'Test Run "{test_run_name}" deleted successfully!')
        return redirect('test_cases:test_run_list')
    
    return render(request, 'test_runs/confirm_delete.html', {'test_run': test_run})


@login_required
def test_run_execute(request, pk):
    test_run = get_object_or_404(TestRun, pk=pk, created_by=request.user)
    executions = test_run.test_executions.all().order_by('testcase__priority', 'id')
    
    if request.method == 'POST':
        execution_id = request.POST.get('execution_id')
        if execution_id:
            execution = get_object_or_404(TestExecution, id=execution_id, test_run=test_run)
            form = TestExecutionForm(request.POST, instance=execution)
            if form.is_valid():
                execution = form.save(commit=False)
                execution.executor = request.user
                if execution.status != 'not_executed':
                    execution.execution_date = timezone.now()
                execution.save()
                messages.success(request, 'Execution result recorded successfully!')
                return redirect('test_cases:test_run_execute', pk=pk)
    
    context = {
        'test_run': test_run,
        'executions': executions,
        'summary': test_run.get_execution_summary(),
    }
    return render(request, 'test_runs/execute.html', context)


# Test Execution Views
@login_required
def test_execution_dashboard(request):
    # Get user's test executions
    user_projects = Project.objects.filter(created_by=request.user)
    user_testcases = TestCase.objects.filter(user_story__epic__project__in=user_projects)
    executions = TestExecution.objects.filter(testcase__in=user_testcases)
    
    # Calculate metrics
    total_executions = executions.count()
    recent_executions = executions.filter(
        execution_date__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Status distribution
    status_counts = {}
    for status, label in TestExecution.STATUS_CHOICES:
        status_counts[label] = executions.filter(status=status).count()
    
    # Pass rate calculation
    executed_tests = executions.exclude(status__in=['not_executed', 'in_progress'])
    passed_tests = executed_tests.filter(status='passed')
    pass_rate = (passed_tests.count() / executed_tests.count() * 100) if executed_tests.count() > 0 else 0
    
    # Average execution time
    avg_execution_time = executions.filter(
        execution_time_minutes__isnull=False
    ).aggregate(avg_time=Avg('execution_time_minutes'))['avg_time'] or 0
    
    # Recent executions for timeline
    recent_timeline = executions.filter(
        execution_date__isnull=False
    ).order_by('-execution_date')[:10]
    
    context = {
        'total_executions': total_executions,
        'recent_executions': recent_executions,
        'status_counts': status_counts,
        'pass_rate': round(pass_rate, 1),
        'avg_execution_time': round(avg_execution_time, 1),
        'recent_timeline': recent_timeline,
    }
    return render(request, 'test_execution/dashboard.html', context)


@login_required
def test_execution_detail(request, pk):
    execution = get_object_or_404(TestExecution, pk=pk)
    
    # Check user access
    if execution.testcase.user_story.epic.project.created_by != request.user:
        messages.error(request, 'You do not have permission to access this execution.')
        return redirect('test_cases:test_execution_dashboard')
    
    execution_steps = execution.execution_steps.all().order_by('step_number')
    
    if request.method == 'POST':
        form = TestExecutionForm(request.POST, instance=execution)
        if form.is_valid():
            execution = form.save(commit=False)
            execution.executor = request.user
            if execution.status != 'not_executed':
                execution.execution_date = timezone.now()
            execution.save()
            messages.success(request, 'Execution updated successfully!')
            return redirect('test_cases:test_execution_detail', pk=pk)
    else:
        form = TestExecutionForm(instance=execution)
    
    context = {
        'execution': execution,
        'execution_steps': execution_steps,
        'form': form,
    }
    return render(request, 'test_execution/detail.html', context)


@login_required
def test_execution_record(request, pk):
    execution = get_object_or_404(TestExecution, pk=pk)
    
    # Check user access
    if execution.testcase.user_story.epic.project.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        form = TestExecutionForm(request.POST, instance=execution)
        if form.is_valid():
            execution = form.save(commit=False)
            execution.executor = request.user
            if execution.status != 'not_executed':
                execution.execution_date = timezone.now()
            execution.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Execution recorded successfully',
                'status': execution.get_status_display(),
                'execution_date': execution.execution_date.strftime('%Y-%m-%d %H:%M') if execution.execution_date else None
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def test_execution_report(request):
    user_projects = Project.objects.filter(created_by=request.user)
    user_testcases = TestCase.objects.filter(user_story__epic__project__in=user_projects)
    executions = TestExecution.objects.filter(testcase__in=user_testcases)
    
    form = TestExecutionReportForm(request.GET, user=request.user)
    
    if form.is_valid():
        # Apply filters
        if form.cleaned_data['date_from']:
            executions = executions.filter(execution_date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data['date_to']:
            executions = executions.filter(execution_date__lte=form.cleaned_data['date_to'])
        if form.cleaned_data['project']:
            executions = executions.filter(testcase__user_story__epic__project=form.cleaned_data['project'])
        if form.cleaned_data['epic']:
            executions = executions.filter(testcase__user_story__epic=form.cleaned_data['epic'])
        if form.cleaned_data['status']:
            executions = executions.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['executor']:
            executions = executions.filter(executor=form.cleaned_data['executor'])
    
    # Pagination
    paginator = Paginator(executions.order_by('-execution_date'), 20)
    page_number = request.GET.get('page')
    executions = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'executions': executions,
    }
    return render(request, 'test_execution/report.html', context)


@login_required
def test_execution_export(request):
    user_projects = Project.objects.filter(created_by=request.user)
    user_testcases = TestCase.objects.filter(user_story__epic__project__in=user_projects)
    executions = TestExecution.objects.filter(testcase__in=user_testcases)
    
    # Apply same filters as report
    form = TestExecutionReportForm(request.GET, user=request.user)
    if form.is_valid():
        if form.cleaned_data['date_from']:
            executions = executions.filter(execution_date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data['date_to']:
            executions = executions.filter(execution_date__lte=form.cleaned_data['date_to'])
        if form.cleaned_data['project']:
            executions = executions.filter(testcase__user_story__epic__project=form.cleaned_data['project'])
        if form.cleaned_data['epic']:
            executions = executions.filter(testcase__user_story__epic=form.cleaned_data['epic'])
        if form.cleaned_data['status']:
            executions = executions.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['executor']:
            executions = executions.filter(executor=form.cleaned_data['executor'])
    
    try:
        from .utils import generate_execution_excel_report
        response = generate_execution_excel_report(executions.order_by('-execution_date'))
        return response
    except ImportError:
        messages.error(request, "Excel export functionality is not available.")
        return redirect('test_cases:test_execution_report')


@login_required 
@require_POST
def bulk_test_execution(request):
    form = BulkTestExecutionForm(request.POST, user=request.user)
    
    if form.is_valid():
        test_cases = form.cleaned_data['test_cases']
        status = form.cleaned_data['status']
        comments = form.cleaned_data['comments']
        
        # Get or create a test run for bulk execution
        test_run, created = TestRun.objects.get_or_create(
            name=f"Bulk Execution - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            created_by=request.user,
            defaults={'status': 'in_progress'}
        )
        
        updated_count = 0
        for testcase in test_cases:
            execution, created = TestExecution.objects.get_or_create(
                testcase=testcase,
                test_run=test_run,
                defaults={
                    'status': status,
                    'executor': request.user,
                    'execution_date': timezone.now(),
                    'comments': comments
                }
            )
            if not created:
                execution.status = status
                execution.executor = request.user
                execution.execution_date = timezone.now()
                execution.comments = comments
                execution.save()
            updated_count += 1
        
        messages.success(request, f'Successfully updated {updated_count} test case executions!')
        return JsonResponse({'success': True, 'message': f'Updated {updated_count} executions'})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})


# Test Suite Views
@login_required
def test_suite_list(request):
    test_suites = TestSuite.objects.filter(created_by=request.user).order_by('-created_date')
    
    # Filter by project
    project_id = request.GET.get('project')
    if project_id:
        user_epics = Epic.objects.filter(project_id=project_id, project__created_by=request.user)
        user_stories = UserStory.objects.filter(epic__in=user_epics)
        user_testcases = TestCase.objects.filter(user_story__in=user_stories)
        test_suites = test_suites.filter(test_cases__in=user_testcases).distinct()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        test_suites = test_suites.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(test_suites, 10)
    page_number = request.GET.get('page')
    test_suites = paginator.get_page(page_number)
    
    # Get projects for filter
    projects = Project.objects.filter(created_by=request.user)
    
    context = {
        'test_suites': test_suites,
        'projects': projects,
        'selected_project': project_id,
        'search_query': search_query,
    }
    return render(request, 'test_suites/list.html', context)


@login_required
def test_suite_create(request):
    if request.method == 'POST':
        form = TestSuiteForm(request.POST, user=request.user)
        if form.is_valid():
            test_suite = form.save(commit=False)
            test_suite.created_by = request.user
            test_suite.save()
            form.save_m2m()
            messages.success(request, 'Test Suite created successfully!')
            return redirect('test_cases:test_suite_list')
    else:
        form = TestSuiteForm(user=request.user)
    
    return render(request, 'test_suites/form.html', {
        'form': form,
        'title': 'Create Test Suite',
        'action': 'Create'
    })


@login_required
def test_suite_edit(request, pk):
    test_suite = get_object_or_404(TestSuite, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = TestSuiteForm(request.POST, instance=test_suite, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test Suite updated successfully!')
            return redirect('test_cases:test_suite_list')
    else:
        form = TestSuiteForm(instance=test_suite, user=request.user)
    
    return render(request, 'test_suites/form.html', {
        'form': form,
        'title': 'Edit Test Suite',
        'action': 'Update',
        'test_suite': test_suite
    })


@login_required
def test_suite_delete(request, pk):
    test_suite = get_object_or_404(TestSuite, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        suite_name = test_suite.name
        test_suite.delete()
        messages.success(request, f'Test Suite "{suite_name}" deleted successfully!')
        return redirect('test_cases:test_suite_list')
    
    return render(request, 'test_suites/confirm_delete.html', {'test_suite': test_suite})


# Additional AJAX Views
@login_required
def get_test_cases_by_filters(request):
    project_id = request.GET.get('project_id')
    epic_id = request.GET.get('epic_id')
    story_id = request.GET.get('story_id')
    
    testcases = TestCase.objects.filter(user_story__epic__project__created_by=request.user)
    
    if project_id:
        testcases = testcases.filter(user_story__epic__project_id=project_id)
    if epic_id:
        testcases = testcases.filter(user_story__epic_id=epic_id)
    if story_id:
        testcases = testcases.filter(user_story_id=story_id)
    
    data = [{
        'id': tc.id, 
        'name': tc.name,
        'priority': tc.priority,
        'status': tc.status
    } for tc in testcases]
    return JsonResponse(data, safe=False)


@login_required
def get_execution_stats(request):
    test_run_id = request.GET.get('test_run_id')
    if not test_run_id:
        return JsonResponse({'error': 'Test run ID required'}, status=400)
    
    test_run = get_object_or_404(TestRun, pk=test_run_id, created_by=request.user)
    summary = test_run.get_execution_summary()
    
    return JsonResponse(summary)