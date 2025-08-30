from queue import Full
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from rest_framework import generics, status, filters
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import transaction, models
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Sum, Q, Prefetch
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from django.core.exceptions import ValidationError

from project.enum import Status
from project.models import Project, Task, TimeEntry
from .serializers import (
    ProjectSerializer, ProjectListSerializer, TaskSerializer,
    TaskCreateUpdateSerializer, TimeEntrySerializer, DashboardSerializer
)
from .filters import ProjectFilter, TaskFilter

logger = logging.getLogger(__name__)

@extend_schema(
    description="List all projects or create a new project. Supports pagination, search by title/description, and filtering by various parameters.",
    responses={
        200: ProjectListSerializer(many=True),
        201: ProjectSerializer,
        400: OpenApiTypes.OBJECT,
        429: OpenApiTypes.OBJECT
    },
    parameters=[
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search projects by title or description (case-insensitive partial match)",
            examples=[
                OpenApiExample("Search by title", value="Website"),
                OpenApiExample("Search by description", value="e-commerce")
            ]
        ),
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order results by: title, created, updated. Use '-' prefix for descending order (e.g., '-created')",
            examples=[
                OpenApiExample("Order by title ascending", value="title"),
                OpenApiExample("Order by created descending", value="-created")
            ]
        )
    ],
    request=ProjectSerializer
)
class ProjectListCreateView(generics.ListCreateAPIView):
    """
    List all projects with pagination, search, and filtering.
    Create new projects.
    """
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user"
    filterset_class = ProjectFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created', 'updated']
    ordering = ['-created']
    
    def get_queryset(self):
        """Optimized queryset with prefetch for task counts."""
        return Project.objects.prefetch_related(
            Prefetch(
                'tasks',
                queryset=Task.objects.select_related('project')
            )
        ).annotate(
            task_count_db=Count('tasks')
        )
    
    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == 'GET':
            return ProjectListSerializer
        return ProjectSerializer

@extend_schema(
    description="Retrieve, update, or delete a specific project by ID.",
    responses={
        200: ProjectSerializer,
        404: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        429: OpenApiTypes.OBJECT
    },
    request=ProjectSerializer,
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="UUID of the project to retrieve/update/delete",
            required=True
        )
    ]
)
class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific project.
    """
    serializer_class = ProjectSerializer
    lookup_field = 'id'
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user"
    
    def get_queryset(self):
        """Optimized queryset with related data."""
        return Project.objects.prefetch_related(
            Prefetch(
                'tasks',
                queryset=Task.objects.select_related('project').prefetch_related(
                    'time_entries'
                )
            )
        )

@extend_schema(
    description="List all tasks or create a new task. Supports pagination, search by title/description, and filtering by status, project, etc.",
    responses={
        200: TaskSerializer(many=True),
        201: TaskCreateUpdateSerializer,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
        429: OpenApiTypes.OBJECT
    },
    parameters=[
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search tasks by title or description (case-insensitive partial match)",
            examples=[
                OpenApiExample("Search by title", value="Backend"),
                OpenApiExample("Search by description", value="API")
            ]
        ),
        OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order results by: title, status, created, updated. Use '-' prefix for descending order",
            examples=[
                OpenApiExample("Order by status ascending", value="status"),
                OpenApiExample("Order by created descending", value="-created")
            ]
        )
    ],
    request=TaskCreateUpdateSerializer
)
class TaskListCreateView(generics.ListCreateAPIView):
    """
    List all tasks with filtering and search capabilities.
    Create new tasks.
    """
    filterset_class = TaskFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'status', 'created', 'updated']
    ordering = ['-created']
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user"
    
    def get_queryset(self):
        """Optimized queryset with select_related and prefetch_related."""
        return Task.objects.select_related('project').prefetch_related(
            'time_entries'
        )
    
    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == 'POST':
            return TaskCreateUpdateSerializer
        return TaskSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Create task with proper transaction handling."""
        project_id = serializer.validated_data.pop('project_id')
        try:
            project = Project.objects.get(id=project_id)
            serializer.save(project=project)
        except Project.DoesNotExist:
            raise ValidationError({'project_id': 'Project not found.'})

@extend_schema(
    description="Retrieve, update, or delete a specific task by ID.",
    responses={
        200: TaskSerializer,
        201: TaskCreateUpdateSerializer,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
        429: OpenApiTypes.OBJECT
    },
    request=TaskCreateUpdateSerializer,
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="UUID of the task to retrieve/update/delete",
            required=True
        )
    ]
)
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific task.
    """
    lookup_field = 'id'
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user"
    
    def get_queryset(self):
        """Optimized queryset with related data."""
        return Task.objects.select_related('project').prefetch_related(
            'time_entries'
        )
    
    def get_serializer_class(self):
        """Use different serializers for update."""
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateUpdateSerializer
        return TaskSerializer

@extend_schema(
    methods=['POST'],
    description="Start a timer for a specific task. Creates a new time entry and updates task status to 'In Progress' if currently 'To Do'.",
    request=None,
    responses={
        201: TimeEntrySerializer,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
        429: OpenApiTypes.OBJECT
    },
    parameters=[
        OpenApiParameter(
            name='task_id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="UUID of the task to start timer for",
            required=True
        )
    ],
    examples=[
        OpenApiExample(
            "Successful response",
            summary="Timer started successfully",
            value={
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "start_time": "2025-08-30T08:40:00Z",
                "end_time": "null",
                "duration": "null"
            },
            status_codes=["201"]
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def start_timer(request, task_id: str) -> Response:
    """Start a timer for a specific task."""
    try:
        task = Task.objects.select_for_update().get(id=task_id)
        
        # Check if task already has an active timer
        if task.has_active_timer:
            return Response(
                {'error': 'Task already has an active timer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new time entry
        time_entry = TimeEntry.objects.create(
            task=task,
            start_time=timezone.now()
        )
        
        # Update task status to In Progress if it's Todo
        if task.status == Status.TODO:
            task.status = Status.IN_PROGRESS
            task.save(update_fields=['status'])
        
        # Clear relevant cache
        cache.delete(f'dashboard_metrics')
        cache.delete(f'project_{task.project.id}_metrics')
        
        serializer = TimeEntrySerializer(time_entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Task.DoesNotExist:
        return Response(
            {'error': 'Task not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error starting timer for task {task_id}: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    methods=['POST'],
    description="Stop the active timer for a specific task. Updates the time entry with end time and duration, and updates task's total spent time.",
    request=None,
    responses={
        200: TimeEntrySerializer,
        400: OpenApiTypes.OBJECT,
        404: OpenApiTypes.OBJECT,
        429: OpenApiTypes.OBJECT
    },
    parameters=[
        OpenApiParameter(
            name='task_id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description="UUID of the task to stop timer for",
            required=True
        )
    ],
    examples=[
        OpenApiExample(
            "Successful response",
            summary="Timer stopped successfully",
            value={
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "start_time": "2025-08-30T08:40:00Z",
                "end_time": "2025-08-30T09:40:00Z",
                "duration": "01:00:00"
            },
            status_codes=["200"]
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def stop_timer(request, task_id: str) -> Response:
    """Stop the active timer for a specific task."""
    try:
        task = Task.objects.select_for_update().get(id=task_id)
        
        # Get active timer
        active_timer = task.active_timer
        if not active_timer:
            return Response(
                {'error': 'No active timer found for this task'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Stop the timer
        end_time = timezone.now()
        active_timer.end_time = end_time
        active_timer.duration = end_time - active_timer.start_time
        active_timer.save()
        
        # Update task's spent time
        task.spent_time += active_timer.duration
        task.save(update_fields=['spent_time'])
        
        # Clear relevant cache
        cache.delete(f'dashboard_metrics')
        cache.delete(f'project_{task.project.id}_metrics')
        
        serializer = TimeEntrySerializer(active_timer)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Task.DoesNotExist:
        return Response(
            {'error': 'Task not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error stopping timer for task {task_id}: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@extend_schema(
    methods=['GET'],
    description="Retrieve dashboard overview with aggregate metrics including task counts by status, total estimated/spent time, and time spent per project. Supports optional date range filtering.",
    responses={
        200: DashboardSerializer,
        400: OpenApiTypes.OBJECT,
        429: OpenApiTypes.OBJECT
    },
    parameters=[
        OpenApiParameter(
            name='start_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="Start date for filtering time entries (format: YYYY-MM-DD)",
            examples=[
                OpenApiExample("Start date example", value="2025-08-01")
            ]
        ),
        OpenApiParameter(
            name='end_date',
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            description="End date for filtering time entries (format: YYYY-MM-DD)",
            examples=[
                OpenApiExample("End date example", value="2025-08-30")
            ]
        )
    ],
    examples=[
        OpenApiExample(
            "Successful response",
            summary="Dashboard overview data",
            value={
                "task_counts": {
                    "TODO": 5,
                    "IN_PROGRESS": 3,
                    "DONE": 10
                },
                "total_estimated_time": "50:30",
                "total_spent_time": "45:15",
                "time_spent_per_project": [
                    {
                        "project_id": "123e4567-e89b-12d3-a456-426614174000",
                        "project_title": "Website Redesign",
                        "spent_time": "25:45"
                    }
                ],
                "date_range_filter": {
                    "start_date": "2025-08-01",
                    "end_date": "2025-08-30"
                }
            },
            status_codes=["200"]
        )
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_overview(request) -> Response:
    """
    Get dashboard overview with efficient aggregate queries and caching.
    """
    # Get date range filters
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # Create cache key based on filters
    cache_key = f"dashboard_metrics_{start_date}_{end_date}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response(cached_data, status=status.HTTP_200_OK)
    
    try:
        # Base querysets
        tasks_qs = Task.objects.all()
        time_entries_qs = TimeEntry.objects.select_related('task__project')
        
        # Apply date range filtering if provided
        date_filter = {}
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                time_entries_qs = time_entries_qs.filter(
                    start_time__date__gte=start_date_obj
                )
                date_filter['start_date'] = start_date
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                time_entries_qs = time_entries_qs.filter(
                    start_time__date__lte=end_date_obj
                )
                date_filter['end_date'] = end_date
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Task counts per status
        task_counts = dict(
            tasks_qs.values('status').annotate(
                count=Count('id')
            ).values_list('status', 'count')
        )
        
        # Fill in missing statuses with 0
        for status_choice, _ in Status.choices:
            task_counts.setdefault(status_choice, 0)
        
        # Total estimated and spent time
        time_aggregates = tasks_qs.aggregate(
            total_estimated=Sum('estimated_time'),
            total_spent=Sum('spent_time')
        )
        
        # Format time durations
        def format_duration(duration: Optional[timedelta]) -> str:
            if not duration:
                return "00:00"
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes = remainder // 60
            return f"{hours:02d}:{minutes:02d}"
        
        # Time spent per project (with date filtering if applied)
        project_time_query = Project.objects.annotate(
            spent_time_sum=Sum('tasks__spent_time')
        ).values('id', 'title', 'spent_time_sum')
        
        if start_date or end_date:
            # For date-filtered queries, we need to sum from time entries
            project_time_data = []
            projects = Project.objects.prefetch_related('tasks').all()
            
            for project in projects:
                project_entries = time_entries_qs.filter(
                    task__project=project,
                    end_time__isnull=False
                )
                total_duration = project_entries.aggregate(
                    total=Sum('duration')
                )['total'] or timedelta()
                
                project_time_data.append({
                    'project_id': str(project.id),
                    'project_title': project.title,
                    'spent_time': format_duration(total_duration)
                })
        else:
            project_time_data = [
                {
                    'project_id': str(project['id']),
                    'project_title': project['title'],
                    'spent_time': format_duration(project['spent_time_sum'])
                }
                for project in project_time_query
            ]
        
        # Prepare response data
        data = {
            'task_counts': task_counts,
            'total_estimated_time': format_duration(time_aggregates['total_estimated']),
            'total_spent_time': format_duration(time_aggregates['total_spent']),
            'time_spent_per_project': project_time_data,
        }
        
        if date_filter:
            data['date_range_filter'] = date_filter
        
        # Cache the results for 5 minutes
        cache.set(cache_key, data, 300)
        
        serializer = DashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating dashboard overview: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )