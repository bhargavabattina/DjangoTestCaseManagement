from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Project, Epic, UserStory, TestCase, TestRun, TestExecution, TestExecutionStep, TestSuite


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError("Project name must be at least 3 characters long.")
        return name


class EpicForm(forms.ModelForm):
    class Meta:
        model = Epic
        fields = ['name', 'description', 'status', 'project']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['project'].queryset = Project.objects.filter(created_by=user)
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError("Epic name must be at least 3 characters long.")
        return name



class UserStoryForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_project'}),
        help_text="Select the project first",
        required=True
    )
    epic = forms.ModelChoiceField(
        queryset=Epic.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_epic'}),
        help_text="Select an epic after choosing a project",
        required=True  # Epic is required
    )

    class Meta:
        model = UserStory
        fields = ['name', 'description', 'acceptance_criteria', 'status',
                  'priority', 'story_points', 'project', 'epic', 'assigned_to']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'acceptance_criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'story_points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Filter projects by the current user
            self.fields['project'].queryset = Project.objects.filter(created_by=user)

            # Handle epic queryset
            if self.instance and self.instance.pk and self.instance.epic:
                # For editing, set project and epic querysets based on the instance
                self.fields['project'].initial = self.instance.epic.project
                self.fields['epic'].queryset = Epic.objects.filter(project=self.instance.epic.project)
                self.fields['epic'].initial = self.instance.epic
            else:
                # For new user stories, set epic queryset based on submitted project
                if 'project' in self.data:
                    try:
                        project_id = int(self.data.get('project'))
                        self.fields['epic'].queryset = Epic.objects.filter(project_id=project_id)
                    except (ValueError, TypeError):
                        self.fields['epic'].queryset = Epic.objects.none()
                else:
                    self.fields['epic'].queryset = Epic.objects.none()

            # Set assigned_to queryset
            self.fields['assigned_to'].queryset = User.objects.all()
            self.fields['assigned_to'].empty_label = "Unassigned"

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get('project')
        epic = cleaned_data.get('epic')

        if project and epic:
            # Validate that the epic belongs to the selected project
            if epic.project != project:
                raise ValidationError({
                    'epic': "The selected epic does not belong to the chosen project."
                })
        elif project and not epic:
            # Require an epic since it's mandatory
            raise ValidationError({
                'epic': "Please select an epic for the chosen project."
            })

        return cleaned_data

    def save(self, commit=True):
        user_story = super().save(commit=False)

        # Ensure the epic is set from cleaned_data
        if self.cleaned_data.get('epic'):
            user_story.epic = self.cleaned_data['epic']

        if commit:
            user_story.save()
            self.save_m2m()

        return user_story





class TestCaseForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_project'}),
        help_text="Select the project first",
        required=True
    )
    epic = forms.ModelChoiceField(
        queryset=Epic.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_epic'}),
        help_text="Select the epic after choosing a project",
        required=True
    )
    user_story = forms.ModelChoiceField(
        queryset=UserStory.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_user_story'}),
        help_text="Select the user story after choosing an epic",
        required=True
    )

    class Meta:
        model = TestCase
        fields = ['name', 'description', 'test_steps', 'expected_results', 'status',
                  'execution_status', 'priority', 'is_automated', 'project', 'epic',
                  'user_story', 'assigned_to']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'test_steps': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'required': True}),
            'expected_results': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'execution_status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'is_automated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.user = user  # Store user for validation
        super().__init__(*args, **kwargs)

        if user:
            # Filter projects by the current user
            self.fields['project'].queryset = Project.objects.filter(created_by=user)

            # Handle epic and user story querysets
            if self.instance and self.instance.pk and self.instance.user_story:
                # For editing, set initial values and querysets based on the instance
                self.fields['project'].initial = self.instance.user_story.epic.project
                self.fields['epic'].initial = self.instance.user_story.epic
                self.fields['epic'].queryset = Epic.objects.filter(project=self.instance.user_story.epic.project)
                self.fields['user_story'].initial = self.instance.user_story
                self.fields['user_story'].queryset = UserStory.objects.filter(epic=self.instance.user_story.epic)
            else:
                # For new test cases, set querysets based on submitted data
                if 'project' in self.data:
                    try:
                        project_id = int(self.data.get('project'))
                        self.fields['epic'].queryset = Epic.objects.filter(project_id=project_id)
                    except (ValueError, TypeError):
                        self.fields['epic'].queryset = Epic.objects.none()
                else:
                    self.fields['epic'].queryset = Epic.objects.none()

                if 'epic' in self.data:
                    try:
                        epic_id = int(self.data.get('epic'))
                        self.fields['user_story'].queryset = UserStory.objects.filter(epic_id=epic_id)
                    except (ValueError, TypeError):
                        self.fields['user_story'].queryset = UserStory.objects.none()
                else:
                    self.fields['user_story'].queryset = UserStory.objects.none()

            # Set assigned_to queryset
            self.fields['assigned_to'].queryset = User.objects.all()
            self.fields['assigned_to'].empty_label = "Unassigned"
        else:
            raise ValueError("User must be provided to initialize the form.")

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 5:
            raise ValidationError("Test case name must be at least 5 characters long.")
        return name

    def clean_test_steps(self):
        test_steps = self.cleaned_data.get('test_steps')
        if len(test_steps.strip()) < 10:
            raise ValidationError("Test steps must be at least 10 characters long.")
        return test_steps

    def clean_expected_results(self):
        expected_results = self.cleaned_data.get('expected_results')
        if len(expected_results.strip()) < 10:
            raise ValidationError("Expected results must be at least 10 characters long.")
        return expected_results

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get('project')
        epic = cleaned_data.get('epic')
        user_story = cleaned_data.get('user_story')

        # Ensure all fields are provided
        if not project:
            self.add_error('project', "A project is required for this test case.")
        if not epic:
            self.add_error('epic', "An epic is required for this test case.")
        if not user_story:
            self.add_error('user_story', "A user story is required for this test case.")

        # Validate relationships
        if project and epic and epic.project_id != project.id:
            self.add_error('epic', "Selected epic does not belong to the selected project.")
        if epic and user_story and user_story.epic_id != epic.id:
            self.add_error('user_story', "Selected user story does not belong to the selected epic.")

        # Ensure project and epic are consistent with user story
        if user_story:
            cleaned_data['epic'] = user_story.epic
            cleaned_data['project'] = user_story.epic.project
            self.cleaned_data['epic'] = user_story.epic
            self.cleaned_data['project'] = user_story.epic.project
        elif epic:
            cleaned_data['project'] = epic.project
            self.cleaned_data['project'] = epic.project

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        user_story = self.cleaned_data.get('user_story')

        if user_story:
            instance.user_story = user_story
            instance.epic = user_story.epic
            instance.project = user_story.epic.project

        # Defer created_by to the view to avoid conflicts
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls',
            'required': True
        }),
        help_text="Upload an Excel file (.xlsx or .xls format)"
    )
    
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        help_text="Select the project for imported test cases"
    )
    
    epic = forms.ModelChoiceField(
        queryset=Epic.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        help_text="Select the epic for imported test cases"
    )
    
    user_story = forms.ModelChoiceField(
        queryset=UserStory.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        help_text="Select the user story for imported test cases"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['project'].queryset = Project.objects.filter(created_by=user)
    
    def clean_excel_file(self):
        excel_file = self.cleaned_data.get('excel_file')
        if excel_file:
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                raise ValidationError("Only Excel files (.xlsx, .xls) are allowed.")
            
            # Check file size (limit to 10MB)
            if excel_file.size > 10 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 10MB.")
        
        return excel_file


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Password'



class TestRunForm(forms.ModelForm):
    test_cases = forms.ModelMultipleChoiceField(
        queryset=TestCase.objects.none(),
        widget=forms.MultipleHiddenInput(attrs={'id': 'id_test_cases'}),
        required=False
    )

    class Meta:
        model = TestRun
        fields = ['name', 'description', 'status', 'scheduled_date', 'test_cases']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)
        if user:
            # Filter test cases by user (test cases linked to user-owned projects)
            self.fields['test_cases'].queryset = TestCase.objects.filter(
                user_story__epic__project__created_by=user
            )
        else:
            self.fields['test_cases'].queryset = TestCase.objects.none()

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 5:
            raise ValidationError("Test run name must be at least 5 characters long.")
        return name

class TestExecutionForm(forms.ModelForm):
    execution_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datepicker',
            'type': 'datetime-local',
        })
    )
    
    class Meta:
        model = TestExecution
        fields = ['status', 'execution_date', 'comments', 'execution_time_minutes', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'execution_time_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def clean_execution_time_minutes(self):
        execution_time = self.cleaned_data.get('execution_time_minutes')
        if execution_time is not None and execution_time < 0:
            raise ValidationError("Execution time cannot be negative.")
        return execution_time


class TestExecutionStepForm(forms.ModelForm):
    execution_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datepicker',
            'type': 'datetime-local',
        })
    )
    
    class Meta:
        model = TestExecutionStep
        fields = ['step_description', 'expected_result', 'actual_result', 'status', 'execution_date', 'comments']
        widgets = {
            'step_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'required': True}),
            'expected_result': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'required': True}),
            'actual_result': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class TestSuiteForm(forms.ModelForm):
    test_cases = forms.ModelMultipleChoiceField(
        queryset=TestCase.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
        required=True,
        help_text="Select test cases to include in this suite"
    )
    
    class Meta:
        model = TestSuite
        fields = ['name', 'description', 'test_cases']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            user_projects = Project.objects.filter(created_by=user)
            user_epics = Epic.objects.filter(project__in=user_projects)
            user_stories = UserStory.objects.filter(epic__in=user_epics)
            self.fields['test_cases'].queryset = TestCase.objects.filter(user_story__in=user_stories)
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError("Test suite name must be at least 3 characters long.")
        return name


class TestExecutionReportForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'type': 'date',
            'placeholder': 'From Date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'type': 'date',
            'placeholder': 'To Date'
        })
    )
    
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        empty_label="All Projects",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    epic = forms.ModelChoiceField(
        queryset=Epic.objects.all(),
        required=False,
        empty_label="All Epics",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(TestExecution.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    executor = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="All Executors",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            user_projects = Project.objects.filter(created_by=user)
            self.fields['project'].queryset = user_projects
            
            if self.is_bound and self.data.get('project'):
                project_id = self.data.get('project')
                self.fields['epic'].queryset = Epic.objects.filter(project_id=project_id)
            else:
                self.fields['epic'].queryset = Epic.objects.filter(project__in=user_projects)
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError("From date cannot be after to date.")
            
        return cleaned_data


class BulkTestExecutionForm(forms.Form):
    test_cases = forms.ModelMultipleChoiceField(
        queryset=TestCase.objects.all(),
        widget=forms.MultipleHiddenInput(),
        required=True
    )
    
    status = forms.ChoiceField(
        choices=TestExecution.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    comments = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        test_run = kwargs.pop('test_run', None)
        super().__init__(*args, **kwargs)
        
        if user and test_run:
            # Filter test cases based on user permissions and test run
            executions = TestExecution.objects.filter(test_run=test_run)
            self.fields['test_cases'].queryset = TestCase.objects.filter(
                id__in=executions.values_list('testcase', flat=True)
            )