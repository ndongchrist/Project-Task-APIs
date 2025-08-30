from django.db import models
from project.enum import Status
from users.models import ProjectAPIBaseModel
from datetime import timedelta
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from typing import Dict, Any, Optional
from datetime import timedelta
import uuid

# Create your models here.

class Project(ProjectAPIBaseModel):
    """Project model with optimized queries and caching considerations."""
    
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['created']),
        ]
    
    def __str__(self) -> str:
        return self.title
    
    @property
    def task_count(self) -> int:
        """Get total task count for this project."""
        return self.tasks.count()
    
    @property
    def total_estimated_time(self) -> timedelta:
        """Get total estimated time for all tasks in this project."""
        return self.tasks.aggregate(
            total=models.Sum('estimated_time')
        )['total'] or timedelta()
    
    @property
    def total_spent_time(self) -> timedelta:
        """Get total spent time for all tasks in this project."""
        return self.tasks.aggregate(
            total=models.Sum('spent_time')
        )['total'] or timedelta()
        

class Task(ProjectAPIBaseModel):
    """Task model with status tracking and time management."""
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        db_index=True
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.TODO,
        db_index=True
    )
    estimated_time = models.DurationField(
        default=timedelta(),
        validators=[MinValueValidator(timedelta())]
    )
    spent_time = models.DurationField(
        default=timedelta(),
        validators=[MinValueValidator(timedelta())]
    )
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['title']),
            models.Index(fields=['status']),
            models.Index(fields=['created']),
        ]
    
    def __str__(self) -> str:
        return f"{self.project.title} - {self.title}"
    
    @property
    def has_active_timer(self) -> bool:
        """Check if task has an active timer."""
        return self.time_entries.filter(end_time__isnull=True).exists()
    
    @property
    def active_timer(self) -> Optional['TimeEntry']:
        """Get the active timer for this task."""
        return self.time_entries.filter(end_time__isnull=True).first()
    
    
class TimeEntry(ProjectAPIBaseModel):
    """Time tracking entries for tasks."""
    
    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE, 
        related_name='time_entries',
        db_index=True
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['task', 'start_time']),
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['task'],
                condition=models.Q(end_time__isnull=True),
                name='unique_active_timer_per_task'
            )
        ]
    
    def __str__(self) -> str:
        status = "Active" if self.end_time is None else f"Duration: {self.duration}"
        return f"{self.task.title} - {status}"
    
    def save(self, *args, **kwargs) -> None:
        """Override save to calculate duration and update task spent time."""
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)
        
    @property
    def is_active(self) -> bool:
        """Check if this time entry is currently active."""
        return self.end_time is None