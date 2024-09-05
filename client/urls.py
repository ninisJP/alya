from django.urls import path
from .views import index_client

urlpatterns = [
    path('', index_client, name='index_client')
]
