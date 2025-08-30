from django.urls import path
from project.api.api import *

app_name = 'project'

urlpatterns = [
    # Project endpoints
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<uuid:id>/', ProjectDetailView.as_view(), name='project-detail'),

    # Task endpoints
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<uuid:id>/', TaskDetailView.as_view(), name='task-detail'),
    
    # Timer endpoints
    path('tasks/<uuid:task_id>/start-timer/', start_timer, name='start-timer'),
    path('tasks/<uuid:task_id>/stop-timer/', stop_timer, name='stop-timer'),
    
    # Dashboard endpoint
    path('dashboard/', dashboard_overview, name='dashboard-overview'),
]