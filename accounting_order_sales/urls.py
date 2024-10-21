from django.urls import path
from accounting_order_sales.forms import supplier_autocomplete
from .views import purchase_renditions, purchase_conciliations, salesorder, create_salesorder, edit_salesorder, delete_salesorder, items_salesorder, edit_purchase_order, general_purchaseorder, quick_create_purchaseorder, petty_cash, index_bank,edit_bank,delete_bank,bank_statements,BankStatementUploadView, AccountingRequirementOrderListView, accounting_requirement_order_detail_view, update_requirement_order_items, update_requirement_order_state
from . import views

urlpatterns = [
    path("", salesorder, name='salesorder' ),
    # bank
    path('banks/', index_bank, name='bank_index'),
    path('banks/editar/<int:bank_id>/', edit_bank, name='edit_bank'),
    path('banks/eliminar/<int:bank_id>/', delete_bank, name='delete_bank'),
    # bank_statements
    path('banks/<int:bank_id>/statements/', bank_statements, name='bank_statement'),
    # upload statements
    path('banks/upload-statements/', BankStatementUploadView.as_view(), name='upload_bank_statements'),
    path("general_purchaseorder/", general_purchaseorder, name='general_purchaseorder'),
    # purchases reconcilations
    path("reconciliations/", purchase_conciliations, name='purchase_conciliations'),
    # purchases renditions
    path("renditions/", purchase_renditions, name='purchase_renditions'),
    # logistic requirements to accounting
    path('requirement-orders-accounting/', AccountingRequirementOrderListView.as_view(), name='requirement_orders_accounting'),
    path('requirement-order/detail/<int:pk>/', accounting_requirement_order_detail_view, name='requirement_order_detail_accounting'),
    path('requirement-order/update-items/<int:pk>/', update_requirement_order_items, name='update_requirement_order_items'),
    path('requirement-order/update-state/<int:pk>/', update_requirement_order_state, name='update_requirement_order_state'),

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
    path('supplier-autocomplete/', supplier_autocomplete, name='supplier_autocomplete'),
    
    # pettycash
    path('caja_chica/', petty_cash, name='petty_cash'),
]

urlpatterns += htmxurlpatters
