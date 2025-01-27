# See LICENSE file for copyright and license details.
"""
Task Note urls
"""
from django.urls import path
from .views import task_wall

urlpatterns = [
    path('task-wall/', task_wall, name='task-wall'),
]
