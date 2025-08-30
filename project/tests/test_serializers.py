# project/tests/test_serializers.py
from project.api.serializers import TaskSerializer, ProjectSerializer, TimeEntrySerializer
import pytest

@pytest.mark.django_db
def test_task_serializer(task):
    serializer = TaskSerializer(task)
    data = serializer.data
    assert data["title"] == "Test Task"
    assert "estimated_time_hours" in data
    assert data["estimated_time_hours"] == "02:00"

@pytest.mark.django_db
def test_project_serializer(project, task):
    serializer = ProjectSerializer(project)
    data = serializer.data
    assert data["title"] == "Test Project"
    assert data["task_count"] == 1
    assert "total_estimated_time_hours" in data

@pytest.mark.django_db
def test_timeentry_serializer(active_time_entry):
    serializer = TimeEntrySerializer(active_time_entry)
    data = serializer.data
    assert "is_active" in data
    assert data["is_active"] is True
