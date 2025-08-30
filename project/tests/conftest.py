# project/tests/conftest.py
import pytest
from django.utils import timezone
from datetime import timedelta
from project.models import Project, Task, TimeEntry

@pytest.fixture
def project():
    return Project.objects.create(title="Test Project", description="A sample project")

@pytest.fixture
def task(project):
    return Task.objects.create(
        project=project,
        title="Test Task",
        description="Task description",
        estimated_time=timedelta(hours=2)
    )

@pytest.fixture
def active_time_entry(task):
    return TimeEntry.objects.create(
        task=task,
        start_time=timezone.now()
    )
