from django.urls import path
from accounting_order_sales.forms import supplier_autocomplete
from .views import delete_purchase_order, purchase_renditions, purchase_conciliations, salesorder, create_salesorder, edit_salesorder, delete_salesorder, items_salesorder, edit_purchase_order, general_purchaseorder, quick_create_purchaseorder, petty_cash, index_bank,edit_bank,delete_bank,bank_statements,BankStatementUploadView, AccountingRequirementOrderListView, accounting_requirement_order_detail_view, update_requirement_order_items, update_requirement_order_state, report_conciliations, update_field
from . import views
from . import views_bank

urlpatterns = [
    path("", salesorder, name='salesorder' ),
    # bank
    path('banks/', index_bank, name='bank_index'),
    path('banks/editar/<int:bank_id>/', edit_bank, name='edit_bank'),
    path('banks/eliminar/<int:bank_id>/', delete_bank, name='delete_bank'),
    # bank_loans
    path('banks/loans/', views.bank_loans, name='bank_loans'),
    # bank_statements
    path('banks/<int:bank_id>/statements/', bank_statements, name='bank_statement'),
    # upload statements
    path('banks/upload-statements/', BankStatementUploadView.as_view(), name='upload_bank_statements'),
    path("general_purchaseorder/", general_purchaseorder, name='general_purchaseorder'),
    # purchases reconcilations
    path("reconciliations/", purchase_conciliations, name='purchase_conciliations'),
    path("report_conciliations", report_conciliations, name='report_conciliations'),
    path('update-field/<int:item_id>/', update_field, name='update_field'),
    # purchases renditions
    path("renditions/", purchase_renditions, name='purchase_renditions'),
    path('add-rendition/', views.add_rendition, name='add_rendition'),
    # logistic requirements to accounting
    path('requirement-orders-accounting/', AccountingRequirementOrderListView.as_view(), name='requirement_orders_accounting'),
    path('requirement-order/detail/<int:pk>/', accounting_requirement_order_detail_view, name='requirement_order_detail_accounting'),
    path('requirement-order/update-items/<int:pk>/', update_requirement_order_items, name='update_requirement_order_items'),
    path('requirement-order/update-state/<int:pk>/', update_requirement_order_state, name='update_requirement_order_state'),
    path('ajax/load-suppliers/', views.ajax_load_suppliers, name='ajax_load_suppliers'),

    # collection orders
    path('collection_orders/', views.collection_orders, name='collection_orders'),
    path('collection_orders/<int:salesorder_id>/', views.collection_order_detail, name='collection_order_detail'),
    path('collection_orders/<int:collection_order_id>/delete/', views.delete_collection_order, name='delete_collection_order'),
    path('collection_orders/<int:collection_order_id>/edit/', views.edit_collection_order, name='edit_collection_order'),
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
    path('eliminar_ordencompra/<int:order_id>/', delete_purchase_order, name='delete_purchase_order'),

    # pettycash
    path('caja_chica/', petty_cash, name='petty_cash'),
    path('petty_cash_state/', views.petty_cash_state, name='petty_cash_state'),
    path('update_payment_status/<int:item_id>/', views.update_payment_status, name='update_payment_status'),


    # ajax concilations
    path('assign_bank_statement/<int:item_id>/<int:statement_id>/', views.assign_bank_statement, name='assign_bank_statement'),


    # Bank
    path('banks/loan/', views_bank.loan_main, name='bank_loan_index'),
    path('banks/loan/new/', views_bank.loan_new, name='bank_loan_new'),
    path('banks/loan/new/coutas/<int:couta_id>/', views_bank.loan_edit_coutas, name='bank_loan_form_coutas'),
    path('banks/loan/see/<int:loan_id>/', views_bank.loan_see, name='bank_loan_see'),
    path('banks/loan/pay/<int:loan_id>/', views_bank.loan_pay, name='bank_loan_pay'),
]

urlpatterns += htmxurlpatters
