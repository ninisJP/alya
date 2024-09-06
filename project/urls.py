from django.urls import path

from .views import new_project, list_project

urlpatterns = [
    path('list', list_project, name='project_list'),
    path('new', new_project, name='project_new'),
]
