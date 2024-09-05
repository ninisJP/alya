from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Login.as_view(), name='login'),
    path("register/", views.RegisterView.as_view(), name="register"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
