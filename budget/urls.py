from django.urls import path
from .views import index_budget

urlpatterns = [
    path('', index_budget, name='index_budget')
]
