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
    
    # AJAX URLs for dynamic dropdowns
    path('ajax/epics-by-project/', views.get_epics_by_project, name='get_epics_by_project'),
    path('ajax/stories-by-epic/', views.get_stories_by_epic, name='get_stories_by_epic'),
]
