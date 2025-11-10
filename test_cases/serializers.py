from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Project, Epic, UserStory, TestCase, TestSuite,
    TestRun, TestExecution, TestExecutionStep
)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    epics_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'created_by',
            'created_date', 'updated_date', 'epics_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_date', 'updated_date']

    def get_epics_count(self, obj):
        return obj.epics.count()


class EpicSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    stories_count = serializers.SerializerMethodField()

    class Meta:
        model = Epic
        fields = [
            'id', 'name', 'description', 'status', 'project', 'project_name',
            'created_by', 'created_date', 'updated_date', 'stories_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_date', 'updated_date', 'project_name']

    def get_stories_count(self, obj):
        return obj.user_stories.count()


class UserStorySerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_to', write_only=True, required=False, allow_null=True
    )
    epic_name = serializers.CharField(source='epic.name', read_only=True)
    project_name = serializers.CharField(source='epic.project.name', read_only=True)
    testcases_count = serializers.SerializerMethodField()

    class Meta:
        model = UserStory
        fields = [
            'id', 'name', 'description', 'acceptance_criteria', 'status',
            'priority', 'story_points', 'epic', 'epic_name', 'project_name',
            'created_by', 'assigned_to', 'assigned_to_id', 'created_date',
            'updated_date', 'testcases_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_date', 'updated_date']

    def get_testcases_count(self, obj):
        return obj.test_cases.count()


class TestCaseSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assigned_to', write_only=True, required=False, allow_null=True
    )
    user_story_name = serializers.CharField(source='user_story.name', read_only=True)
    epic_name = serializers.CharField(source='user_story.epic.name', read_only=True)
    project_name = serializers.CharField(source='user_story.epic.project.name', read_only=True)

    class Meta:
        model = TestCase
        fields = [
            'id', 'name', 'description', 'test_steps', 'expected_results',
            'status', 'execution_status', 'priority', 'is_automated',
            'user_story', 'user_story_name', 'epic_name', 'project_name',
            'created_by', 'assigned_to', 'assigned_to_id', 'created_date',
            'updated_date', 'last_executed'
        ]
        read_only_fields = ['id', 'created_by', 'created_date', 'updated_date']


class TestCaseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing test cases"""
    user_story_name = serializers.CharField(source='user_story.name', read_only=True)
    project_name = serializers.CharField(source='user_story.epic.project.name', read_only=True)

    class Meta:
        model = TestCase
        fields = [
            'id', 'name', 'status', 'execution_status', 'priority',
            'is_automated', 'user_story_name', 'project_name'
        ]


class TestSuiteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    test_cases = TestCaseListSerializer(many=True, read_only=True)
    test_case_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=TestCase.objects.all(), write_only=True, source='test_cases'
    )
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = TestSuite
        fields = [
            'id', 'name', 'description', 'test_cases', 'test_case_ids',
            'created_by', 'created_date', 'statistics'
        ]
        read_only_fields = ['id', 'created_by', 'created_date']

    def get_statistics(self, obj):
        return obj.get_test_case_statistics()


class TestExecutionStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestExecutionStep
        fields = [
            'id', 'test_execution', 'step_number', 'step_description',
            'expected_result', 'actual_result', 'status', 'execution_date', 'comments'
        ]
        read_only_fields = ['id']


class TestExecutionSerializer(serializers.ModelSerializer):
    executor = UserSerializer(read_only=True)
    testcase = TestCaseSerializer(read_only=True)
    testcase_id = serializers.PrimaryKeyRelatedField(
        queryset=TestCase.objects.all(), source='testcase', write_only=True
    )
    execution_steps = TestExecutionStepSerializer(many=True, read_only=True)

    class Meta:
        model = TestExecution
        fields = [
            'id', 'testcase', 'testcase_id', 'test_run', 'executor', 'status',
            'execution_date', 'comments', 'execution_time_minutes', 'notes',
            'execution_steps'
        ]
        read_only_fields = ['id', 'executor']


class TestExecutionCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating test executions"""
    class Meta:
        model = TestExecution
        fields = [
            'id', 'testcase', 'test_run', 'status', 'execution_date',
            'comments', 'execution_time_minutes', 'notes'
        ]
        read_only_fields = ['id']


class TestRunSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    test_executions = TestExecutionSerializer(many=True, read_only=True)
    execution_summary = serializers.SerializerMethodField()

    class Meta:
        model = TestRun
        fields = [
            'id', 'name', 'description', 'status', 'created_by',
            'created_date', 'updated_date', 'scheduled_date',
            'test_executions', 'execution_summary'
        ]
        read_only_fields = ['id', 'created_by', 'created_date', 'updated_date']

    def get_execution_summary(self, obj):
        return obj.get_execution_summary()


class TestRunListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing test runs"""
    created_by = UserSerializer(read_only=True)
    execution_summary = serializers.SerializerMethodField()

    class Meta:
        model = TestRun
        fields = [
            'id', 'name', 'status', 'created_by', 'created_date',
            'scheduled_date', 'execution_summary'
        ]

    def get_execution_summary(self, obj):
        return obj.get_execution_summary()


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    projects_count = serializers.IntegerField()
    epics_count = serializers.IntegerField()
    stories_count = serializers.IntegerField()
    testcases_count = serializers.IntegerField()
    test_runs_count = serializers.IntegerField()
    test_suites_count = serializers.IntegerField()
    total_executions = serializers.IntegerField()
    passed_executions = serializers.IntegerField()
    pass_rate = serializers.FloatField()
    recent_executions_count = serializers.IntegerField()
