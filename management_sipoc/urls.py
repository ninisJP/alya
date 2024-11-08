from django.urls import path
from . import views

urlpatterns = [
    # Rutas principales
    path('sipocs/', views.list_sipocs, name='list_sipocs'),  # Vista para listar todos los SIPOCs
    path('sipocs/create/', views.create_sipoc, name='create_sipoc'),  # Vista para crear un nuevo SIPOC
    path('sipocs/<int:sipoc_id>/', views.detail_sipoc, name='detail_sipoc'),  # Vista de detalle para un SIPOC específico
    
    # Rutas de htmx para manipulación de filas y edición
    path('sipocs/<int:sipoc_id>/add-row/', views.add_row, name='add_row'),
    path('sipocs/<int:sipoc_id>/add-empty-row/', views.add_empty_row, name='add_empty_row'),
    path('sipocs/<int:row_id>/edit/', views.edit_row, name='edit_row'),
    path('sipocs/<int:row_id>/delete/', views.delete_row, name='delete_row'),
    
    # Rutas para edición de campos individuales
    path('sipocs/<int:row_id>/edit/suppliers/', views.edit_suppliers, name='edit_suppliers'),
    path('sipocs/<int:row_id>/edit/inputs/', views.edit_inputs, name='edit_inputs'),
    path('sipocs/<int:row_id>/edit/processes/', views.edit_processes, name='edit_processes'),
    path('sipocs/<int:row_id>/edit/outputs/', views.edit_outputs, name='edit_outputs'),
    path('sipocs/<int:row_id>/edit/customers/', views.edit_customers, name='edit_customers'),

    # Rutas para crear nuevos elementos
    path('sipocs/<int:row_id>/add-supplier/', views.add_supplier, name='add_supplier'),
    path('sipocs/<int:row_id>/add-input/', views.add_input, name='add_input'),
    path('sipocs/<int:row_id>/add-process/', views.add_process, name='add_process'),
    path('sipocs/<int:row_id>/add-output/', views.add_output, name='add_output'),
    path('sipocs/<int:row_id>/add-customer/', views.add_customer, name='add_customer'),
    path('sipoc/row/<int:row_id>/cancel/', views.cancel_edit_row, name='cancel_edit_row'),
    
    # Rutas para flujogramas
    path('suppliers/<int:sipoc_id>/', views.supplier_list, name='supplier_list'),
    path('inputs/<int:sipoc_id>/', views.input_list, name='input_list'),
    path('processes/<int:sipoc_id>/', views.process_list, name='process_list'),
    path('outputs/<int:sipoc_id>/', views.output_list, name='output_list'),
    path('customers/<int:sipoc_id>/', views.customer_list, name='customer_list'),
    
  
]
