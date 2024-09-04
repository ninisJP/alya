from django.urls import path
from .views import HomeCC

urlpatterns = [
     path('', HomeCC, name='follow_control_home'),
]
