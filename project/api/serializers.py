from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from typing import Dict, Any
from project.models import Project, Task, TimeEntry

class TimeEntrySerializer(serializers.ModelSerializer):
    """Serializer for time entries with validation."""
    
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = TimeEntry
        fields = [
            'id', 'start_time', 'end_time', 'duration', 
            'is_active', 'created'
        ]
        read_only_fields = ['duration', 'created', 'updated']
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate time entry data."""
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if end_time and start_time and end_time <= start_time:
            raise serializers.ValidationError(
                "End time must be after start time."
            )
        
        return attrs

class TaskSerializer(serializers.ModelSerializer):
    """Comprehensive task serializer with time tracking."""
    
    has_active_timer = serializers.ReadOnlyField()
    active_timer = TimeEntrySerializer(read_only=True)
    time_entries = TimeEntrySerializer(many=True, read_only=True)
    estimated_time_hours = serializers.SerializerMethodField()
    spent_time_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 
            'estimated_time', 'spent_time', 'estimated_time_hours',
            'spent_time_hours', 'has_active_timer', 'active_timer',
            'time_entries', 'created'
        ]
        read_only_fields = ['spent_time', 'created', 'updated']
    
    def get_estimated_time_hours(self, obj: Task) -> str:
        """Convert estimated time to HH:MM format."""
        total_seconds = int(obj.estimated_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        return f"{hours:02d}:{minutes:02d}"
    
    def get_spent_time_hours(self, obj: Task) -> str:
        """Convert spent time to HH:MM format."""
        total_seconds = int(obj.spent_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        return f"{hours:02d}:{minutes:02d}"

class TaskCreateUpdateSerializer(TaskSerializer):
    """Serializer for creating and updating tasks."""
    
    project_id = serializers.UUIDField(write_only=True)
    
    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ['project_id']
        read_only_fields = [
            'spent_time', 'has_active_timer', 'active_timer',
            'time_entries', 'created'
        ]

class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer with task summary information."""
    
    task_count = serializers.ReadOnlyField()
    total_estimated_time_hours = serializers.SerializerMethodField()
    total_spent_time_hours = serializers.SerializerMethodField()
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'task_count',
            'total_estimated_time_hours', 'total_spent_time_hours',
            'tasks', 'created'
        ]
        read_only_fields = ['created', 'updated']
    
    def get_total_estimated_time_hours(self, obj: Project) -> str:
        """Convert total estimated time to HH:MM format."""
        total_seconds = int(obj.total_estimated_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        return f"{hours:02d}:{minutes:02d}"
    
    def get_total_spent_time_hours(self, obj: Project) -> str:
        """Convert total spent time to HH:MM format."""
        total_seconds = int(obj.total_spent_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        return f"{hours:02d}:{minutes:02d}"

class ProjectListSerializer(ProjectSerializer):
    """Lightweight project serializer for list views."""
    
    class Meta(ProjectSerializer.Meta):
        fields = [
            'id', 'title', 'description', 'task_count',
            'total_estimated_time_hours', 'total_spent_time_hours',
            'created'
        ]

class DashboardSerializer(serializers.Serializer):
    """Dashboard overview serializer."""
    
    task_counts = serializers.DictField(child=serializers.IntegerField())
    total_estimated_time = serializers.CharField()
    total_spent_time = serializers.CharField()
    time_spent_per_project = serializers.ListField(
        child=serializers.DictField()
    )
    date_range_filter = serializers.DictField(required=False)