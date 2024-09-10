from django.urls import path

from .views import project_index

urlpatterns = [
    path('', project_index, name='project_index'),
]
