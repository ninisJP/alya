from django.urls import path
from .views import index_portal

urlpatterns = [
    path('', index_portal, name='index_portal')
]
