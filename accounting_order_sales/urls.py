from django.urls import path
from .views import salesorder, create_salesorder, edit_salesorder, delete_salesorder, items_salesorder, edit_purchase_order, general_purchaseorder, quick_create_purchaseorder, petty_cash
from . import views

urlpatterns = [
    path("", salesorder, name='salesorder' ),
    path("general_purchaseorder/", general_purchaseorder, name='general_purchaseorder')
]

htmxurlpatters = [
    path('crear-ordenventa/', create_salesorder, name='create-salesorder' ),
    path('editar-ordenventa/<int:salesorder_id>/', edit_salesorder, name='edit-salesorder'),
    path('eliminar-ordenventa/<int:salesorder_id>/', delete_salesorder, name='delete-salesorder'),
    path('items-ordenventa/<int:salesorder_id>/', items_salesorder , name='item-salesorder'),
    
    # purchase order
    path('salesorder/<int:salesorder_id>/quick-create-purchase-order/', quick_create_purchaseorder, name='quick_create_purchaseorder'),
    path('salesorder/<int:salesorder_id>/purchase-orders/', views.purchase_orders, name='purchaseorders'),
    path('editar_ordencompra/<int:order_id>/', edit_purchase_order, name='edit_purchase_order'),
    
    # pettycash
    path('caja_chica/', petty_cash, name='petty_cash'),
]

urlpatterns += htmxurlpatters