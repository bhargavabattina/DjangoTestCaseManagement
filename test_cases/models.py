from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('completed', 'Completed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_date']
        
    def __str__(self):
        return self.name


class Epic(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='epics')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_epics')
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_date']
        
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class UserStory(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('testing', 'Testing'),
        ('done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    acceptance_criteria = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    story_points = models.IntegerField(null=True, blank=True)
    epic = models.ForeignKey(Epic, on_delete=models.CASCADE, related_name='user_stories')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_stories')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_stories')
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_date']
        verbose_name_plural = "User Stories"
        
    def __str__(self):
        return f"{self.epic.project.name} - {self.epic.name} - {self.name}"


class TestCase(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('ready', 'Ready'),
        ('blocked', 'Blocked'),
    ]
    
    EXECUTION_STATUS_CHOICES = [
        ('not_executed', 'Not Executed'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    test_steps = models.TextField()
    expected_results = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    execution_status = models.CharField(max_length=20, choices=EXECUTION_STATUS_CHOICES, default='not_executed')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    is_automated = models.BooleanField(default=False)
    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE, related_name='test_cases')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_testcases')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_testcases')
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    last_executed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_date']
        
    def __str__(self):
        return f"{self.user_story.epic.project.name} - {self.user_story.name} - {self.name}"


class TestSuite(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    test_cases = models.ManyToManyField(TestCase, related_name='test_suites')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_test_suites')
    created_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_date']
        verbose_name_plural = "Test Suites"
    
    def __str__(self):
        return self.name

    def get_test_case_statistics(self):
        """Get statistics about test cases in this suite"""
        test_cases = self.test_cases.all()
        
        stats = {
            'total': test_cases.count(),
            'critical': test_cases.filter(priority='critical').count(),
            'high': test_cases.filter(priority='high').count(),
            'medium': test_cases.filter(priority='medium').count(),
            'low': test_cases.filter(priority='low').count(),
            'automated': test_cases.filter(is_automated=True).count(),
            'manual': test_cases.filter(is_automated=False).count(),
            'ready': test_cases.filter(status='ready').count(),
            'draft': test_cases.filter(status='draft').count(),
            'blocked': test_cases.filter(status='blocked').count(),
        }
        
        return stats


class TestRun(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_test_runs')
    created_date = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField(auto_now=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_date']
        verbose_name_plural = "Test Runs"

    def __str__(self):
        return self.name

    def get_execution_summary(self):
        summary = {
            'passed': self.test_executions.filter(status='passed').count(),
            'failed': self.test_executions.filter(status='failed').count(),
            'skipped': self.test_executions.filter(status='skipped').count(),
            'blocked': self.test_executions.filter(status='blocked').count(),
            'in_progress': self.test_executions.filter(status='in_progress').count(),
            'not_executed': self.test_executions.filter(status='not_executed').count(),
        }

        total = sum(summary.values())
        summary['total'] = total

        # Calculate percentages
        if total > 0:
            summary['passed_percentage'] = round((summary['passed'] / total) * 100, 1)
            summary['failed_percentage'] = round((summary['failed'] / total) * 100, 1)
            summary['skipped_percentage'] = round((summary['skipped'] / total) * 100, 1)
            summary['blocked_percentage'] = round((summary['blocked'] / total) * 100, 1)
        else:
            summary['passed_percentage'] = 0
            summary['failed_percentage'] = 0
            summary['skipped_percentage'] = 0
            summary['blocked_percentage'] = 0

        return summary

class TestExecution(models.Model):
    STATUS_CHOICES = [
        ('not_executed', 'Not Executed'),
        ('in_progress', 'In Progress'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
        ('blocked', 'Blocked'),
    ]

    testcase = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='test_executions')
    test_run = models.ForeignKey(TestRun, on_delete=models.CASCADE, related_name='test_executions')
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='test_executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_executed')
    execution_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    execution_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['testcase__priority', 'execution_date']
        verbose_name_plural = "Test Executions"

    def __str__(self):
        return f"{self.test_run.name} - {self.testcase.name} - {self.get_status_display()}"


class TestExecutionStep(models.Model):
    STATUS_CHOICES = [
        ('not_executed', 'Not Executed'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    test_execution = models.ForeignKey(TestExecution, on_delete=models.CASCADE, related_name='execution_steps')
    step_number = models.PositiveIntegerField()
    step_description = models.TextField()
    expected_result = models.TextField()
    actual_result = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_executed')
    execution_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    
    class Meta:
        ordering = ['test_execution', 'step_number']
        verbose_name_plural = "Test Execution Steps"
    
    def __str__(self):
        return f"{self.test_execution.testcase.name} - Step {self.step_number}"