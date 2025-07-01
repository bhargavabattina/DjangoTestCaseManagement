from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Project, Epic, UserStory, TestCase
from .forms import (
    ProjectForm, EpicForm, UserStoryForm, TestCaseForm, 
    ExcelUploadForm, UserRegistrationForm, UserLoginForm
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