from django.contrib import admin
from .models import Project, Epic, UserStory, TestCase

# Register your models here.

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_by', 'created_date', 'updated_date')
    list_filter = ('status', 'created_date', 'updated_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_date', 'updated_date')
    ordering = ('-created_date',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'status', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Epic)
class EpicAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'status', 'created_by', 'created_date', 'updated_date')
    list_filter = ('status', 'project', 'created_date', 'updated_date')
    search_fields = ('name', 'description', 'project__name')
    readonly_fields = ('created_date', 'updated_date')
    ordering = ('-created_date',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'project', 'status', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserStory)
class UserStoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'epic', 'status', 'priority', 'story_points', 'assigned_to', 'created_date')
    list_filter = ('status', 'priority', 'epic__project', 'epic', 'created_date')
    search_fields = ('name', 'description', 'epic__name', 'epic__project__name')
    readonly_fields = ('created_date', 'updated_date')
    ordering = ('-created_date',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'acceptance_criteria', 'epic')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'story_points')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_story', 'status', 'execution_status', 'priority', 'is_automated', 'assigned_to', 'created_date')
    list_filter = ('status', 'execution_status', 'priority', 'is_automated', 'user_story__epic__project', 'user_story__epic', 'created_date')
    search_fields = ('name', 'description', 'user_story__name', 'user_story__epic__name', 'user_story__epic__project__name')
    readonly_fields = ('created_date', 'updated_date', 'last_executed')
    ordering = ('-created_date',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'user_story')
        }),
        ('Test Details', {
            'fields': ('test_steps', 'expected_results')
        }),
        ('Status & Priority', {
            'fields': ('status', 'execution_status', 'priority', 'is_automated')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_date', 'updated_date', 'last_executed'),
            'classes': ('collapse',)
        }),
    )