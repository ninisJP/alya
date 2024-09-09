from django.urls import path
from .views import salesorder, create_salesorder, edit_salesorder, delete_salesorder

urlpatterns = [
    path("", salesorder, name='salesorder' ),
]

htmxurlpatters = [
    path('crear-ordenventa/', create_salesorder, name='create-salesorder' ),
    path('editar-ordenventa/<int:salesorder_id>/', edit_salesorder, name='edit-salesorder'),
    path('eliminar-ordenventa/<int:salesorder_id>/', delete_salesorder, name='delete-salesorder'),
]

urlpatterns += htmxurlpatters