from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Project, Epic, UserStory, TestCase, TestSuite,
    TestRun, TestExecution, TestExecutionStep
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, ProjectSerializer,
    EpicSerializer, UserStorySerializer, TestCaseSerializer,
    TestCaseListSerializer, TestSuiteSerializer, TestRunSerializer,
    TestRunListSerializer, TestExecutionSerializer, TestExecutionCreateSerializer,
    TestExecutionStepSerializer, DashboardStatsSerializer
)


# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return JWT tokens"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for the current user"""
    user = request.user

    # Get basic statistics
    projects_count = Project.objects.filter(created_by=user).count()
    epics_count = Epic.objects.filter(project__created_by=user).count()
    stories_count = UserStory.objects.filter(epic__project__created_by=user).count()
    testcases_count = TestCase.objects.filter(user_story__epic__project__created_by=user).count()
    test_runs_count = TestRun.objects.filter(created_by=user).count()
    test_suites_count = TestSuite.objects.filter(created_by=user).count()

    # Get test execution statistics
    user_projects = Project.objects.filter(created_by=user)
    user_testcases = TestCase.objects.filter(user_story__epic__project__in=user_projects)
    all_executions = TestExecution.objects.filter(testcase__in=user_testcases)

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
    recent_projects = Project.objects.filter(created_by=user).order_by('-created_date')[:5]
    recent_testcases = TestCase.objects.filter(
        user_story__epic__project__created_by=user
    ).order_by('-created_date')[:5]
    recent_executions = all_executions.filter(
        execution_date__isnull=False
    ).order_by('-execution_date')[:5]

    data = {
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
        'recent_projects': ProjectSerializer(recent_projects, many=True).data,
        'recent_testcases': TestCaseListSerializer(recent_testcases, many=True).data,
        'recent_executions': TestExecutionSerializer(recent_executions, many=True).data,
    }

    return Response(data)


# ViewSets
class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Project model"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_date', 'name', 'status']
    ordering = ['-created_date']
    filterset_fields = ['status']

    def get_queryset(self):
        return Project.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def epics(self, request, pk=None):
        """Get all epics for a specific project"""
        project = self.get_object()
        epics = Epic.objects.filter(project=project)
        serializer = EpicSerializer(epics, many=True)
        return Response(serializer.data)


class EpicViewSet(viewsets.ModelViewSet):
    """ViewSet for Epic model"""
    queryset = Epic.objects.all()
    serializer_class = EpicSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_date', 'name', 'status']
    ordering = ['-created_date']
    filterset_fields = ['status', 'project']

    def get_queryset(self):
        return Epic.objects.filter(project__created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def stories(self, request, pk=None):
        """Get all user stories for a specific epic"""
        epic = self.get_object()
        stories = UserStory.objects.filter(epic=epic)
        serializer = UserStorySerializer(stories, many=True)
        return Response(serializer.data)


class UserStoryViewSet(viewsets.ModelViewSet):
    """ViewSet for UserStory model"""
    queryset = UserStory.objects.all()
    serializer_class = UserStorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'acceptance_criteria']
    ordering_fields = ['created_date', 'name', 'priority', 'status']
    ordering = ['-created_date']
    filterset_fields = ['status', 'priority', 'epic', 'epic__project']

    def get_queryset(self):
        return UserStory.objects.filter(epic__project__created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def testcases(self, request, pk=None):
        """Get all test cases for a specific user story"""
        story = self.get_object()
        testcases = TestCase.objects.filter(user_story=story)
        serializer = TestCaseSerializer(testcases, many=True)
        return Response(serializer.data)


class TestCaseViewSet(viewsets.ModelViewSet):
    """ViewSet for TestCase model"""
    queryset = TestCase.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'test_steps']
    ordering_fields = ['created_date', 'name', 'priority', 'status']
    ordering = ['-created_date']
    filterset_fields = [
        'status', 'execution_status', 'priority', 'is_automated',
        'user_story', 'user_story__epic', 'user_story__epic__project'
    ]

    def get_queryset(self):
        return TestCase.objects.filter(user_story__epic__project__created_by=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return TestCaseListSerializer
        return TestCaseSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a test case"""
        testcase = self.get_object()
        execution_status = request.data.get('execution_status')

        if execution_status not in ['passed', 'failed', 'skipped']:
            return Response(
                {'error': 'Invalid execution status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        testcase.execution_status = execution_status
        testcase.last_executed = timezone.now()
        testcase.save()

        serializer = self.get_serializer(testcase)
        return Response(serializer.data)


class TestSuiteViewSet(viewsets.ModelViewSet):
    """ViewSet for TestSuite model"""
    queryset = TestSuite.objects.all()
    serializer_class = TestSuiteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_date', 'name']
    ordering = ['-created_date']

    def get_queryset(self):
        return TestSuite.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def create_test_run(self, request, pk=None):
        """Create a test run from this test suite"""
        suite = self.get_object()
        test_run_name = request.data.get('name')
        test_run_description = request.data.get('description', '')

        if not test_run_name:
            return Response(
                {'error': 'Test run name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create test run
        test_run = TestRun.objects.create(
            name=test_run_name,
            description=test_run_description,
            created_by=request.user,
            status='not_started'
        )

        # Create test executions for all test cases in suite
        for test_case in suite.test_cases.all():
            TestExecution.objects.create(
                testcase=test_case,
                test_run=test_run,
                status='not_executed'
            )

        serializer = TestRunSerializer(test_run)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TestRunViewSet(viewsets.ModelViewSet):
    """ViewSet for TestRun model"""
    queryset = TestRun.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_date', 'name', 'status', 'scheduled_date']
    ordering = ['-created_date']
    filterset_fields = ['status']

    def get_queryset(self):
        return TestRun.objects.filter(created_by=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return TestRunListSerializer
        return TestRunSerializer

    def perform_create(self, serializer):
        test_run = serializer.save(created_by=self.request.user)

        # Create test executions for selected test cases
        test_case_ids = self.request.data.get('test_case_ids', [])
        user_testcases = TestCase.objects.filter(
            id__in=test_case_ids,
            user_story__epic__project__created_by=self.request.user
        )

        for testcase in user_testcases:
            TestExecution.objects.create(
                testcase=testcase,
                test_run=test_run,
                status='not_executed'
            )

    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Get all executions for a test run"""
        test_run = self.get_object()
        executions = test_run.test_executions.all()
        serializer = TestExecutionSerializer(executions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get execution summary for a test run"""
        test_run = self.get_object()
        summary = test_run.get_execution_summary()
        return Response(summary)


class TestExecutionViewSet(viewsets.ModelViewSet):
    """ViewSet for TestExecution model"""
    queryset = TestExecution.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['execution_date', 'status']
    ordering = ['-execution_date']
    filterset_fields = ['status', 'test_run', 'testcase', 'executor']

    def get_queryset(self):
        user_projects = Project.objects.filter(created_by=self.request.user)
        user_testcases = TestCase.objects.filter(user_story__epic__project__in=user_projects)
        return TestExecution.objects.filter(testcase__in=user_testcases)

    def get_serializer_class(self):
        if self.action == 'create':
            return TestExecutionCreateSerializer
        return TestExecutionSerializer

    def perform_create(self, serializer):
        serializer.save(executor=self.request.user)

    def perform_update(self, serializer):
        execution = serializer.save(executor=self.request.user)
        if execution.status != 'not_executed' and not execution.execution_date:
            execution.execution_date = timezone.now()
            execution.save()

    @action(detail=True, methods=['post'])
    def record_result(self, request, pk=None):
        """Record test execution result"""
        execution = self.get_object()
        execution.status = request.data.get('status', execution.status)
        execution.comments = request.data.get('comments', execution.comments)
        execution.execution_time_minutes = request.data.get('execution_time_minutes', execution.execution_time_minutes)
        execution.executor = request.user

        if execution.status != 'not_executed':
            execution.execution_date = timezone.now()

        execution.save()
        serializer = self.get_serializer(execution)
        return Response(serializer.data)


# API endpoint for dynamic dropdowns
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_epics_by_project(request):
    """Get epics filtered by project"""
    project_id = request.query_params.get('project_id')
    if not project_id:
        return Response({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    epics = Epic.objects.filter(project_id=project_id, project__created_by=request.user)
    data = [{'id': epic.id, 'name': epic.name} for epic in epics]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stories_by_epic(request):
    """Get user stories filtered by epic"""
    epic_id = request.query_params.get('epic_id')
    if not epic_id:
        return Response({'error': 'epic_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    stories = UserStory.objects.filter(epic_id=epic_id, epic__project__created_by=request.user)
    data = [{'id': story.id, 'name': story.name} for story in stories]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    """Get all users for assignment"""
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
