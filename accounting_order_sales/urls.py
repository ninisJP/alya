from django.urls import path
from .views import salesorder, create_salesorder, edit_salesorder, delete_salesorder, items_salesorder, update_purchase_orders, edit_purchase_order
from . import views

urlpatterns = [
    path("", salesorder, name='salesorder' ),
]

htmxurlpatters = [
    path('crear-ordenventa/', create_salesorder, name='create-salesorder' ),
    path('editar-ordenventa/<int:salesorder_id>/', edit_salesorder, name='edit-salesorder'),
    path('eliminar-ordenventa/<int:salesorder_id>/', delete_salesorder, name='delete-salesorder'),
    path('items-ordenventa/<int:salesorder_id>/', items_salesorder , name='item-salesorder'),
    
    # purchase order
    path('salesorder/<int:salesorder_id>/purchase-orders/', views.purchase_orders, name='purchaseorders'),
    path('actualizar_orden/<int:item_id>/', update_purchase_orders, name='update_purchase_orders'),
    path('editar_ordencompra/<int:order_id>/', edit_purchase_order, name='edit_purchase_order'),

]

urlpatterns += htmxurlpatters