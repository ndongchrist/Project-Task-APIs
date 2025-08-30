import django_filters
from django.db import models
from project.models import Project, Task
from project.enum import Status

class ProjectFilter(django_filters.FilterSet):
    """Advanced filtering for projects."""
    
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    search = django_filters.CharFilter(method='filter_search')
    task_status = django_filters.ChoiceFilter(
        choices=Status.choices,
        method='filter_by_task_status'
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='gte'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created',
        lookup_expr='lte'
    )
    
    class Meta:
        model = Project
        fields = ['title', 'description']
    
    def filter_search(self, queryset, name, value):
        """Search across title and description."""
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value)
        )
    
    def filter_by_task_status(self, queryset, name, value):
        """Filter projects by their tasks' status."""
        return queryset.filter(tasks__status=value).distinct()

class TaskFilter(django_filters.FilterSet):
    """Advanced filtering for tasks."""
    
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    search = django_filters.CharFilter(method='filter_search')
    status = django_filters.ChoiceFilter(choices=Status.choices)
    project = django_filters.UUIDFilter(field_name='project__id')
    has_active_timer = django_filters.BooleanFilter(method='filter_active_timer')
    
    class Meta:
        model = Task
        fields = ['status', 'project']
    
    def filter_search(self, queryset, name, value):
        """Search across title and description."""
        return queryset.filter(
            models.Q(title__icontains=value) |
            models.Q(description__icontains=value)
        )
    
    def filter_active_timer(self, queryset, name, value):
        """Filter tasks by whether they have active timers."""
        if value:
            return queryset.filter(time_entries__end_time__isnull=True)
        return queryset.exclude(time_entries__end_time__isnull=True)