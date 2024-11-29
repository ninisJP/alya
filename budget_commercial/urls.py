from django.urls import path
from .views import create_commercial_budget, detail_commercial_budget, index_budget_commercial, delete_commercial_budget

urlpatterns = [
    path('index_budget_commercial/', index_budget_commercial, name='index_budget_commercial'),
    path('create_commercial_budget/', create_commercial_budget, name='create_commercial_budget'),
    path('detail_commercial_budget/<int:pk>/', detail_commercial_budget, name='detail_commercial_budget'),
    path('delete_commercial_budget/<int:pk>/', delete_commercial_budget, name='delete_commercial_budget'),

]
