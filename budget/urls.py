from django.urls import path
from .views import index_budget, create_budget, detail_budget, edit_budget, delete_budget

urlpatterns = [
    path('', index_budget, name='index_budget'),
    path('create_budget/', create_budget, name='create_budget'),
    path('detail_budget/<int:pk>/', detail_budget, name='detail_budget'),
    path('edit_budget/<int:pk>/', edit_budget, name='edit_budget'),
    path('delete_budget/<int:pk>/', delete_budget, name='delete_budget'),
]
