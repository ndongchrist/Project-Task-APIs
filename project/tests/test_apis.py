# project/tests/test_apis.py
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from project.models import TimeEntry

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_project_list_create(api_client, project):
    url = reverse("project:project-list-create")
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["results"][0]["title"] == "Test Project"

@pytest.mark.django_db
def test_task_list_create(api_client, project):
    url = reverse("project:task-list-create")
    payload = {
        "title": "API Created Task",
        "description": "From API",
        "estimated_time": "01:00:00",
        "project_id": str(project.id)
    }
    response = api_client.post(url, payload, format="json")
    assert response.status_code == 201
    assert response.data["title"] == "API Created Task"

@pytest.mark.django_db
def test_start_timer(api_client, task):
    url = reverse("project:start-timer", args=[task.id])
    response = api_client.post(url)
    assert response.status_code == 201
    assert TimeEntry.objects.filter(task=task).exists()

@pytest.mark.django_db
def test_stop_timer(api_client, task):
    # first start timer
    start_url = reverse("project:start-timer", args=[task.id])
    api_client.post(start_url)

    stop_url = reverse("project:stop-timer", args=[task.id])
    response = api_client.post(stop_url)
    assert response.status_code == 200
    data = response.data
    assert data["end_time"] is not None

@pytest.mark.django_db
def test_dashboard_overview(api_client):
    url = reverse("project:dashboard-overview")
    response = api_client.get(url)
    assert response.status_code == 200
    assert "task_counts" in response.data
