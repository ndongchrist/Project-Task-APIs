# project/tests/test_models.py
from datetime import timedelta
import pytest


@pytest.mark.django_db
def test_project_str(project):
    assert str(project) == "Test Project"
@pytest.mark.django_db
def test_task_str(task):
    assert str(task) == f"{task.project.title} - {task.title}"

@pytest.mark.django_db
def test_timeentry_str(active_time_entry):
    assert "Active" in str(active_time_entry)

@pytest.mark.django_db
def test_project_task_count(project, task):
    assert project.task_count == 1

@pytest.mark.django_db
def test_project_total_estimated_time(project, task):
    assert project.total_estimated_time == timedelta(hours=2)

@pytest.mark.django_db
def test_task_has_active_timer(task, active_time_entry):
    assert task.has_active_timer is True
    assert task.active_timer == active_time_entry

@pytest.mark.django_db
def test_timeentry_duration_calculation(task, active_time_entry, db):
    active_time_entry.end_time = active_time_entry.start_time + timedelta(hours=1)
    active_time_entry.save()
    assert active_time_entry.duration == timedelta(hours=1)
