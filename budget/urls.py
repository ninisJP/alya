from django.urls import path
from .views import upload_sap_excel, index_budget, delete_budget, export_budget_report, create_sales_order_from_budget, catalog_item_search
from .views_budget import update_budget_partial_plus, detail_budget_plus, budget_item_plus, budget_item_delete, budget_item_update, create_budget_plus
from . import views

urlpatterns = [
    path('', index_budget, name='index_budget'),
    path('budget/<int:budget_id>/upload_sap_excel/', upload_sap_excel, name='upload_sap_excel'),
    # Nueva URL para HTMX
    path('edit-item/<int:item_id>/', views.edit_budget_item_htmx, name='edit_budget_item_htmx'),
    path('delete_budget/<int:pk>/', delete_budget, name='delete_budget'),
    path('duplicate_budget/<int:pk>/', views.duplicate_budget, name='duplicate_budget'),
    path('export_budget/<int:pk>/', export_budget_report, name="export_budget_report"),
    path('create_sales_order/<int:budget_id>/', create_sales_order_from_budget, name='create_sales_order'),
    path('ajax/catalog-item-search/', catalog_item_search, name='catalog_item_search'),
    # Catalog
    path('catalog/', views.catalog, name='budget_catalog'),
    path('catalog/new/', views.catalog_new, name='budget_catalog_new'),
    path('catalog/search/', views.catalog_search, name='budget_catalog_search'),
    path('catalog/edit/<int:catalog_id>/', views.catalog_edit, name='catalog_edit'),
    path('catalog/excel/', views.upload_excel, name='budget_catalog_excel'),
    path('presupuestos/export_catalog/', views.export_catalog, name='export_catalog'),
    # Nueva URL para subir archivo Excel
    path('budget/<int:budget_id>/upload_excel/', views.upload_budget_excel, name='upload_budget_excel'),
    # Budget plus
    path('create_budget_plus', create_budget_plus, name='create_budget_plus'),
    path('detail_budget_plus/<int:pk>/', detail_budget_plus, name='detail_budget_plus'),
    path('budget/<int:pk>/add-item-plus/', budget_item_plus, name='budget_item_plus'),
    path('budget/<int:item_id>/budget_item_delete/', budget_item_delete, name='budget_item_delete'),
    path('budget/<int:pk>/update/', budget_item_update, name='budget_item_update'),
    path('budget/<int:pk>/update-partial/', update_budget_partial_plus, name='update_budget_partial_plus'),
    # TEMPLATE MODEL
    path('descargar-plantilla/', views.download_template, name='descargar_plantilla'),

]