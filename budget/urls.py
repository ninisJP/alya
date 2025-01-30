# See LICENSE file for copyright and license details.
"""
Budget urls
"""
from django.urls import path

from . import views
from . import views_budget


urlpatterns = [
    path('', views.index_budget, name='index_budget'),
    path(
        'budget/<int:budget_id>/upload_sap_excel/',
        views.upload_sap_excel,
        name='upload_sap_excel'
    ),
    # Nueva URL para HTMX
    path(
        'edit-item/<int:item_id>/',
        views.edit_budget_item_htmx,
        name='edit_budget_item_htmx'
    ),
    path(
        'delete_budget/<int:pk>/',
        views.delete_budget,
        name='delete_budget'
    ),
    path(
        'duplicate_budget/<int:pk>/',
        views.duplicate_budget,
        name='duplicate_budget'
    ),
    path(
        'export_budget/<int:pk>/',
        views.export_budget_report,
        name="export_budget_report"
    ),
    path(
        'create_sales_order/<int:budget_id>/',
        views.create_sales_order_from_budget,
        name='create_sales_order'
    ),
    path(
        'ajax/catalog-item-search/',
        views.catalog_item_search,
        name='catalog_item_search'
    ),
    # Catalog
    path('catalog/', views.catalog, name='budget_catalog'),
    path('catalog/new/', views.catalog_new, name='budget_catalog_new'),
    path(
        'catalog/search/',
        views.catalog_search,
        name='budget_catalog_search'
    ),
    path(
        'catalog/edit/<int:catalog_id>/',
        views.catalog_edit,
        name='catalog_edit'
    ),
    path(
        'catalog/excel/',
        views.upload_excel,
        name='budget_catalog_excel'
    ),
    path(
        'presupuestos/export_catalog/',
        views.export_catalog,
        name='export_catalog'
    ),
    # Nueva URL para subir archivo Excel
    path(
        'budget/<int:budget_id>/upload_excel/',
        views.upload_budget_excel,
        name='upload_budget_excel'
    ),
    # Budget plus
    path(
        'create_budget_plus',
        views_budget.create_budget_plus,
        name='create_budget_plus'
    ),
    path(
        'detail_budget_plus/<int:pk>/',
        views_budget.detail_budget_plus,
        name='detail_budget_plus'
    ),
    path(
        'budget/<int:pk>/add-item-plus/',
        views_budget.budget_item_plus,
        name='budget_item_plus'
    ),
    path(
        'budget/<int:item_id>/budget_item_delete/',
        views_budget.budget_item_delete,
        name='budget_item_delete'
    ),
    path(
        'budget/<int:pk>/update/',
        views_budget.budget_item_update,
        name='budget_item_update'
    ),
    path(
        'budget/<int:pk>/update-partial/',
        views_budget.update_budget_partial_plus,
        name='update_budget_partial_plus'
    ),
    # TEMPLATE MODEL
    path(
        'descargar-plantilla/',
        views.download_template,
        name='descargar_plantilla'
    ),
]
