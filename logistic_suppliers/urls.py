from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('suppliers-list/', index_suppliers, name='suppliers'),
]

htmxurlpatters = [
    # tasks urls
    path('create-suppliers/', create_suppliers, name='create-supplier' ),
    path('edit-suppliers/<int:supplier_id>/', edit_suppliers, name='edit-supplier'),
    path('delete-suppliers/<int:supplier_id>/', delete_suppliers, name='delete-supplier'), # Asegúrate de que el nombre sea correcto

]

urlpatterns += htmxurlpatters