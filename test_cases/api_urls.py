from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'projects', api_views.ProjectViewSet, basename='project')
router.register(r'epics', api_views.EpicViewSet, basename='epic')
router.register(r'stories', api_views.UserStoryViewSet, basename='userstory')
router.register(r'testcases', api_views.TestCaseViewSet, basename='testcase')
router.register(r'test-suites', api_views.TestSuiteViewSet, basename='testsuite')
router.register(r'test-runs', api_views.TestRunViewSet, basename='testrun')
router.register(r'test-executions', api_views.TestExecutionViewSet, basename='testexecution')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', api_views.register_user, name='register'),
    path('auth/login/', api_views.login_user, name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', api_views.current_user, name='current_user'),

    # Dashboard
    path('dashboard/stats/', api_views.dashboard_stats, name='dashboard_stats'),

    # Helper endpoints
    path('helpers/epics-by-project/', api_views.get_epics_by_project, name='epics_by_project'),
    path('helpers/stories-by-epic/', api_views.get_stories_by_epic, name='stories_by_epic'),
    path('helpers/users/', api_views.get_users, name='users_list'),

    # Include router URLs
    path('', include(router.urls)),
]
