from django.urls import path
from .views import create_commercial_budget, detail_commercial_budget

urlpatterns = [
    path('create_commercial_budget/', create_commercial_budget, name='create_commercial_budget'),
    path('detail_commercial_budget/<int:pk>/', detail_commercial_budget, name='detail_commercial_budget'),
]
