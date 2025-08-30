from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Task, TimeEntry

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Project model."""
    
    list_display = ['title', 'task_count', 'created']
    list_filter = ['created']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created', 'task_count']
    ordering = ['-created']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Metadata', {
            'fields': ('id', 'task_count', 'created'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Task model."""
    
    list_display = [
        'title', 'project', 'status', 'estimated_time_display',
        'spent_time_display', 'has_active_timer', 'created'
    ]
    list_filter = ['status', 'project', 'created']
    search_fields = ['title', 'description', 'project__title']
    readonly_fields = [
        'id', 'spent_time', 'created',
        'has_active_timer', 'active_timer'
    ]
    ordering = ['-created']
    
    fieldsets = (
        (None, {
            'fields': ('project', 'title', 'description', 'status')
        }),
        ('Time Tracking', {
            'fields': ('estimated_time', 'spent_time', 'has_active_timer', 'active_timer')
        }),
        ('Metadata', {
            'fields': ('id', 'created'),
            'classes': ('collapse',)
        }),
    )
    
    def estimated_time_display(self, obj):
        """Format estimated time for display."""
        total_seconds = int(obj.estimated_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        return f"{hours:02d}:{minutes:02d}"
    estimated_time_display.short_description = "Estimated Time"
    
    def spent_time_display(self, obj):
        """Format spent time for display."""
        total_seconds = int(obj.spent_time.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        return f"{hours:02d}:{minutes:02d}"
    spent_time_display.short_description = "Spent Time"

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    """Enhanced admin interface for TimeEntry model."""
    
    list_display = [
        'task', 'start_time', 'end_time', 'duration_display',
        'is_active', 'created'
    ]
    list_filter = ['start_time', 'end_time', 'task__project']
    search_fields = ['task__title', 'task__project__title']
    readonly_fields = ['id', 'duration', 'is_active', 'created']
    ordering = ['-start_time']
    
    fieldsets = (
        (None, {
            'fields': ('task', 'start_time', 'end_time')
        }),
        ('Computed Fields', {
            'fields': ('duration', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Format duration for display."""
        if not obj.duration:
            return "N/A"
        total_seconds = int(obj.duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        return f"{hours:02d}:{minutes:02d}"
    duration_display.short_description = "Duration"