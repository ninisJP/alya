from django.urls import path
from . import views

urlpatterns = [
    path('', views.candidate_list, name='candidate_list'),
    path('add/', views.add_candidate, name='add_candidate'),
    path('edit/<int:id>/', views.edit_candidate, name='edit_candidate'),
    path('delete/<int:id>/', views.delete_candidate, name='delete_candidate'),
]
