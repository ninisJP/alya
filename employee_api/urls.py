from django.contrib.auth import views as auth_views
from django.urls import path
from .views import login_employee, technician_card, get_technician_card

urlpatterns = [
    path('login_employee/', login_employee, name='login_employee'),
    path('card_employee/', technician_card, name='technician_card'),
    path('get_card_employee/', get_technician_card, name='get_technician_card'),
]
