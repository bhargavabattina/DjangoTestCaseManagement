from django.urls import path
from . import views

app_name = 'test_cases'

urlpatterns = [
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Project URLs
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Epic URLs
    path('epics/', views.epic_list, name='epic_list'),
    path('epics/create/', views.epic_create, name='epic_create'),
    path('epics/<int:pk>/edit/', views.epic_edit, name='epic_edit'),
    path('epics/<int:pk>/delete/', views.epic_delete, name='epic_delete'),
    
    # User Story URLs
    path('stories/', views.story_list, name='story_list'),
    path('stories/create/', views.story_create, name='story_create'),
    path('stories/<int:pk>/edit/', views.story_edit, name='story_edit'),
    path('stories/<int:pk>/delete/', views.story_delete, name='story_delete'),
    
    # Test Case URLs
    path('testcases/', views.testcase_list, name='testcase_list'),
    path('testcases/create/', views.testcase_create, name='testcase_create'),
    path('testcases/<int:pk>/edit/', views.testcase_edit, name='testcase_edit'),
    path('testcases/<int:pk>/delete/', views.testcase_delete, name='testcase_delete'),
    path('testcases/<int:pk>/execute/', views.testcase_execute, name='testcase_execute'),
    
    # Excel Import URLs
    path('testcases/import/', views.testcase_import, name='testcase_import'),
    
    # Test Run URLs
    path('test-runs/', views.test_run_list, name='test_run_list'),
    path('test-runs/create/', views.test_run_create, name='test_run_create'),
    path('test-runs/<int:pk>/edit/', views.test_run_edit, name='test_run_edit'),
    path('test-runs/<int:pk>/delete/', views.test_run_delete, name='test_run_delete'),
    path('test-runs/<int:pk>/execute/', views.test_run_execute, name='test_run_execute'),
    
    # Test Execution URLs
    path('test-execution/dashboard/', views.test_execution_dashboard, name='test_execution_dashboard'),
    path('test-execution/<int:pk>/detail/', views.test_execution_detail, name='test_execution_detail'),
    path('test-execution/<int:pk>/record/', views.test_execution_record, name='test_execution_record'),
    path('test-execution/report/', views.test_execution_report, name='test_execution_report'),
    path('test-execution/export/', views.test_execution_export, name='test_execution_export'),
    
    # Test Suite URLs
    path('test-suites/', views.test_suite_list, name='test_suite_list'),
    path('test-suites/create/', views.test_suite_create, name='test_suite_create'),
    path('test-suites/<int:pk>/edit/', views.test_suite_edit, name='test_suite_edit'),
    path('test-suites/<int:pk>/delete/', views.test_suite_delete, name='test_suite_delete'),
    
    # Bulk Operations URLs
    path('bulk/test-execution/', views.bulk_test_execution, name='bulk_test_execution'),
    
    # AJAX URLs for dynamic dropdowns
    path('ajax/epics-by-project/', views.get_epics_by_project, name='get_epics_by_project'),
    path('ajax/stories-by-epic/', views.get_stories_by_epic, name='get_stories_by_epic'),
    path('ajax/testcases-by-filters/', views.get_test_cases_by_filters, name='get_test_cases_by_filters'),
    path('ajax/execution-stats/', views.get_execution_stats, name='get_execution_stats'),
]