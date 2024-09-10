from django.urls import path
from .views import index_logistic

urlpatterns = [
    path('', index_logistic, name='index_logistic')
    
]
