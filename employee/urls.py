from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path("register/", views.RegisterView.as_view(), name="register"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('list_supervisor/', views.supervisor_list_view, name="supervisor"),
    path('list_technical/', views.technical_list_view, name="technical"),
]
