from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path("register_employee/", views.RegisterView.as_view(), name="register"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('list_supervisor/', views.supervisor_list_view, name="supervisor"),
    path('list_technician/', views.technician_list_view, name="technician"),
    # Edit
    path('supervisor/edit/<int:pk>/', views.edit_supervisor, name='edit_supervisor'),
    path('technician/edit/<int:pk>/', views.edit_technician, name='edit_technician'),


]

