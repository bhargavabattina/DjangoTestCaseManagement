from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Project, Epic, UserStory, TestCase


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
    class Meta:
        model = UserStory
        fields = ['name', 'description', 'acceptance_criteria', 'status', 'priority', 'story_points', 'epic', 'assigned_to']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'acceptance_criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'story_points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'epic': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            user_projects = Project.objects.filter(created_by=user)
            self.fields['epic'].queryset = Epic.objects.filter(project__in=user_projects)
            self.fields['assigned_to'].queryset = User.objects.all()
            self.fields['assigned_to'].empty_label = "Unassigned"
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 5:
            raise ValidationError("User story name must be at least 5 characters long.")
        return name
    
    def clean_story_points(self):
        story_points = self.cleaned_data.get('story_points')
        if story_points is not None and (story_points < 1 or story_points > 100):
            raise ValidationError("Story points must be between 1 and 100.")
        return story_points


class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = ['name', 'description', 'test_steps', 'expected_results', 'status', 'execution_status', 'priority', 'is_automated', 'user_story', 'assigned_to']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'test_steps': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'required': True}),
            'expected_results': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': True}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'execution_status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'is_automated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'user_story': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            user_projects = Project.objects.filter(created_by=user)
            user_epics = Epic.objects.filter(project__in=user_projects)
            self.fields['user_story'].queryset = UserStory.objects.filter(epic__in=user_epics)
            self.fields['assigned_to'].queryset = User.objects.all()
            self.fields['assigned_to'].empty_label = "Unassigned"
    
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
