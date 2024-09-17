from django.urls import path
from .views import index_client, edit_client, delete_client, nav_client

urlpatterns = [
    path('', index_client, name='index_client'),
    path('nav-client/', nav_client, name='nav-client')
]

htmxurlpatters = [

    path('delete-client/<int:client_id>/', delete_client, name='delete-client'),
    path('edit-client/<int:client_id>/', edit_client, name='edit-client'),


]

urlpatterns += htmxurlpatters
