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