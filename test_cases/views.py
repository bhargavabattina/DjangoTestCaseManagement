from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Avg
from datetime import timedelta
from django.template.loader import render_to_string
from django.urls import reverse
from .models import Project, Epic, UserStory, TestCase, TestRun, TestExecution, TestSuite
from .forms import (
    ProjectForm, EpicForm, UserStoryForm, TestCaseForm,
    ExcelUploadForm, UserRegistrationForm, UserLoginForm,
    TestRunForm, TestExecutionForm, TestSuiteForm,
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
            except Exception:
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
    # Get basic statistics
    projects_count = Project.objects.filter(created_by=request.user).count()
    epics_count = Epic.objects.filter(project__created_by=request.user).count()
    stories_count = UserStory.objects.filter(epic__project__created_by=request.user).count()
    testcases_count = TestCase.objects.filter(user_story__epic__project__created_by=request.user).count()

    # Get test execution statistics
    test_runs_count = TestRun.objects.filter(created_by=request.user).count()
    test_suites_count = TestSuite.objects.filter(created_by=request.user).count()

    # Get user's test executions for calculation
    user_projects = Project.objects.filter(created_by=request.user)
    user_testcases = TestCase.objects.filter(user_story__epic__project__in=user_projects)
    all_executions = TestExecution.objects.filter(testcase__in=user_testcases)

    # Calculate test execution metrics
    total_executions = all_executions.count()
    executed_tests = all_executions.exclude(status__in=['not_executed', 'in_progress'])
    passed_executions = executed_tests.filter(status='passed').count()
    pass_rate = (passed_executions / executed_tests.count() * 100) if executed_tests.count() > 0 else 0

    # Recent test executions (last 7 days)
    recent_executions_count = all_executions.filter(
        execution_date__gte=timezone.now() - timedelta(days=7),
        execution_date__isnull=False
    ).count()

    # Get recent activities
    recent_projects = Project.objects.filter(created_by=request.user)[:5]
    recent_testcases = TestCase.objects.filter(user_story__epic__project__created_by=request.user)[:5]
    recent_executions = all_executions.filter(
        execution_date__isnull=False
    ).order_by('-execution_date')[:5]

    context = {
        'projects_count': projects_count,
        'epics_count': epics_count,
        'stories_count': stories_count,
        'testcases_count': testcases_count,
        'test_runs_count': test_runs_count,
        'test_suites_count': test_suites_count,
        'total_executions': total_executions,
        'passed_executions': passed_executions,
        'pass_rate': round(pass_rate, 1),
        'recent_executions_count': recent_executions_count,
        'recent_projects': recent_projects,
        'recent_testcases': recent_testcases,
        'recent_executions': recent_executions,
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
    if not project_id:
        return JsonResponse({'error': 'Project ID is required'}, status=400)
    
    try:
        epics = Epic.objects.filter(project_id=project_id, project__created_by=request.user)
        data = [{'id': epic.id, 'name': epic.name} for epic in epics]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_stories_by_epic(request):
    epic_id = request.GET.get('epic_id')
    if not epic_id:
        return JsonResponse({'error': 'Epic ID is required'}, status=400)
    
    try:
        stories = UserStory.objects.filter(epic_id=epic_id, epic__project__created_by=request.user)
        data = [{'id': story.id, 'name': story.name} for story in stories]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_projects_by_user(request):
    try:
        projects = Project.objects.filter(created_by=request.user)
        data = [{'id': project.id, 'name': project.name} for project in projects]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
def test_run_create_from_suite(request):
    """AJAX endpoint to create test run from suite"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    suite_id = request.POST.get('suite_id')
    test_run_name = request.POST.get('test_run_name')
    test_run_description = request.POST.get('test_run_description', '')

    if not suite_id or not test_run_name:
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    try:
        suite = TestSuite.objects.get(id=suite_id, created_by=request.user)

        # Create test run
        test_run = TestRun.objects.create(
            name=test_run_name,
            description=test_run_description,
            created_by=request.user
        )

        # Create test executions for all test cases in suite
        executions = []
        for test_case in suite.test_cases.all():
            execution = TestExecution.objects.create(
                testcase=test_case,
                test_run=test_run,
                executor=request.user
            )
            executions.append(execution)

        return JsonResponse({
            'success': True,
            'test_run_id': test_run.id,
            'redirect_url': reverse('test_cases:test_run_execute', args=[test_run.id])
        })

    except TestSuite.DoesNotExist:
        return JsonResponse({'error': 'Test suite not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
    all_executions = TestExecution.objects.filter(testcase__in=user_testcases)

    # Calculate metrics
    total_executions = all_executions.count()
    recent_executions = all_executions.filter(
        execution_date__gte=timezone.now() - timedelta(days=30)
    ).count()

    # Status distribution
    status_counts = {}
    for status, label in TestExecution.STATUS_CHOICES:
        status_counts[label] = all_executions.filter(status=status).count()

    # Pass rate calculation
    executed_tests = all_executions.exclude(status__in=['not_executed', 'in_progress'])
    passed_tests = executed_tests.filter(status='passed')
    pass_rate = (passed_tests.count() / executed_tests.count() * 100) if executed_tests.count() > 0 else 0

    # Average execution time
    avg_execution_time = all_executions.filter(
        execution_time_minutes__isnull=False
    ).aggregate(avg_time=Avg('execution_time_minutes'))['avg_time'] or 0

    # Recent executions for timeline
    recent_timeline = all_executions.filter(
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
def test_execution_detail_ajax(request, pk):
    execution = get_object_or_404(TestExecution, pk=pk)

    # Check user access
    if execution.testcase.user_story.epic.project.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get priority color mapping
    priority_colors = {
        'critical': 'danger',
        'high': 'warning',
        'medium': 'primary',
        'low': 'secondary'
    }

    # Get status color mapping
    status_colors = {
        'not_executed': 'secondary',
        'in_progress': 'primary',
        'passed': 'success',
        'failed': 'danger',
        'skipped': 'warning',
        'blocked': 'dark'
    }

    # Parse test steps for step-by-step execution details
    steps = []
    # Prioritize actual execution steps if they exist
    if hasattr(execution, 'execution_steps') and execution.execution_steps.exists():
        for step in execution.execution_steps.all().order_by('step_number'):
            steps.append({
                'number': step.step_number,
                'description': step.description,
                'expected_result': step.expected_result,
                'actual_result': step.actual_result,
                'status': step.get_status_display(),
                'status_color': status_colors.get(step.status, 'secondary'),
                'comments': step.comments
            })

    data = {
        'testcase_name': execution.testcase.name,
        'priority': execution.testcase.get_priority_display(),
        'priority_color': priority_colors.get(execution.testcase.priority, 'secondary'),
        'user_story': execution.testcase.user_story.name,
        'project': execution.testcase.user_story.epic.project.name,
        'status': execution.get_status_display(),
        'status_color': status_colors.get(execution.status, 'secondary'),
        'executor': execution.executor.get_full_name() if execution.executor else 'Unassigned',
        'execution_date': execution.execution_date.strftime('%Y-%m-%d %H:%M') if execution.execution_date else 'Not executed',
        'execution_time': f"{execution.execution_time_minutes} min" if execution.execution_time_minutes else 'N/A',
        'comments': execution.comments or 'No comments',
        'steps': steps
    }

    return JsonResponse(data)


@login_required
def test_execution_summary_data(request):
    user_projects = Project.objects.filter(created_by=request.user)
    user_testcases = TestCase.objects.filter(user_story__epic__project__in=user_projects)
    executions = TestExecution.objects.filter(testcase__in=user_testcases)

    # Apply same filters as report view
    form = TestExecutionReportForm(request.GET, user=request.user)
    form_is_valid = form.is_valid()
    if form_is_valid:
        if form.cleaned_data['date_from']:
            executions = executions.filter(execution_date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data['date_to']:
            # Adjust date_to to include the whole day
            date_to = form.cleaned_data['date_to'] + timedelta(days=1) - timedelta(microseconds=1)
            executions = executions.filter(execution_date__lte=date_to)
        if form.cleaned_data['project']:
            executions = executions.filter(testcase__user_story__epic__project=form.cleaned_data['project'])
        if form.cleaned_data['epic']:
            executions = executions.filter(testcase__user_story__epic=form.cleaned_data['epic'])
        if form.cleaned_data['status']:
            executions = executions.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['executor']:
            executions = executions.filter(executor=form.cleaned_data['executor'])

    # Calculate summary statistics
    status_counts = {}
    for status, _ in TestExecution.STATUS_CHOICES:
        status_counts[status] = executions.filter(status=status).count()

    executed_tests = executions.exclude(status__in=['not_executed', 'in_progress'])
    passed_count = status_counts.get('passed', 0)
    failed_count = status_counts.get('failed', 0)
    pass_rate = (passed_count / executed_tests.count() * 100) if executed_tests.count() > 0 else 0

    # Calculate execution time statistics
    timed_executions = executions.filter(execution_time_minutes__isnull=False)
    avg_execution_time = timed_executions.aggregate(avg_time=Avg('execution_time_minutes'))['avg_time'] or 0
    total_execution_time = sum([e.execution_time_minutes for e in timed_executions if e.execution_time_minutes is not None])

    # Get unique executors count
    unique_executors = executions.exclude(executor__isnull=True).values('executor').distinct().count()

    # Calculate date range
    date_range = "All Time"
    if form_is_valid and (form.cleaned_data['date_from'] or form.cleaned_data['date_to']):
        date_from = form.cleaned_data['date_from'].strftime('%Y-%m-%d') if form.cleaned_data['date_from'] else 'Start'
        display_date_to = (form.cleaned_data['date_to']).strftime('%Y-%m-%d') if form.cleaned_data['date_to'] else 'End'
        date_range = f"{date_from} to {display_date_to}"

    # Generate trends data (last 30 days)
    trends_data = {'labels': [], 'total': [], 'passed': [], 'failed': []}
    # Only generate trends if no date filters are applied, or a general 30-day view is requested
    # If specific date filters are active, trends should be based on that narrow range or suppressed.
    # For this implementation, we will generate trends for the last 30 days if no date filters are present,
    # otherwise, the trends data will be empty.
    if not (form_is_valid and (form.cleaned_data['date_from'] or form.cleaned_data['date_to'])):
        for i in range(29, -1, -1):
            date = timezone.now().date() - timedelta(days=i)
            day_executions = executions.filter(execution_date__date=date)
            trends_data['labels'].append(date.strftime('%m/%d'))
            trends_data['total'].append(day_executions.count())
            trends_data['passed'].append(day_executions.filter(status='passed').count())
            trends_data['failed'].append(day_executions.filter(status='failed').count())

    data = {
        'passed_count': passed_count,
        'failed_count': failed_count,
        'pass_rate': round(pass_rate, 1),
        'avg_execution_time': round(avg_execution_time, 1),
        'total_execution_time': total_execution_time,
        'unique_executors': unique_executors,
        'date_range': date_range,
        'status_distribution': {status: count for status, count in status_counts.items()},
        'trends': trends_data
    }

    return JsonResponse(data)


@login_required
def test_execution_project_breakdown(request):
    user_projects = Project.objects.filter(created_by=request.user)

    projects_data = []
    # Apply same filters as report view, but for each project
    form = TestExecutionReportForm(request.GET, user=request.user)
    form_is_valid = form.is_valid()

    for project in user_projects:
        project_testcases = TestCase.objects.filter(user_story__epic__project=project)
        project_executions = TestExecution.objects.filter(testcase__in=project_testcases)

        if form_is_valid:
            if form.cleaned_data['date_from']:
                project_executions = project_executions.filter(execution_date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data['date_to']:
                date_to = form.cleaned_data['date_to'] + timedelta(days=1) - timedelta(microseconds=1)
                project_executions = project_executions.filter(execution_date__lte=date_to)
            if form.cleaned_data['status']:
                project_executions = project_executions.filter(status=form.cleaned_data['status'])
            if form.cleaned_data['executor']:
                project_executions = project_executions.filter(executor=form.cleaned_data['executor'])

        total_executions = project_executions.count()
        if total_executions > 0:
            executed_tests = project_executions.exclude(status__in=['not_executed', 'in_progress'])
            passed_tests = executed_tests.filter(status='passed')
            pass_rate = (passed_tests.count() / executed_tests.count() * 100) if executed_tests.count() > 0 else 0

            avg_time = project_executions.filter(
                execution_time_minutes__isnull=False
            ).aggregate(avg_time=Avg('execution_time_minutes'))['avg_time'] or 0

            last_execution = project_executions.filter(
                execution_date__isnull=False
            ).order_by('-execution_date').first()

            projects_data.append({
                'id': project.id,
                'name': project.name,
                'total_executions': total_executions,
                'pass_rate': round(pass_rate, 1),
                'avg_time': round(avg_time, 1),
                'last_execution': last_execution.execution_date.strftime('%Y-%m-%d %H:%M') if last_execution else None
            })

    return JsonResponse({'projects': projects_data})


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
            # Adjust date_to to include the whole day
            date_to = form.cleaned_data['date_to'] + timedelta(days=1) - timedelta(microseconds=1)
            executions = executions.filter(execution_date__lte=date_to)
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
            # Adjust date_to to include the whole day
            date_to = form.cleaned_data['date_to'] + timedelta(days=1) - timedelta(microseconds=1)
            executions = executions.filter(execution_date__lte=date_to)
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
def test_suite_stats(request):
    """AJAX endpoint for test suite statistics"""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    test_suites = TestSuite.objects.filter(created_by=request.user)

    suites_data = []
    for suite in test_suites:
        stats = suite.get_test_case_statistics()
        suites_data.append({
            'id': suite.id,
            'name': suite.name,
            'stats': stats,
            'stats_html': render_to_string('test_suites/stats_badges.html', {
                'suite_stats': stats
            }, request=request)
        })

    return JsonResponse({'suites': suites_data})


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