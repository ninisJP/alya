from django.urls import path
from .views import  edit_budget_with_new_item, index_budget, create_budget, detail_budget, edit_budget, delete_budget, catalog, export_budget_report, create_sales_order_from_budget, catalog_item_search
from . import views

urlpatterns = [
    path('', index_budget, name='index_budget'),
    path('create_budget/', create_budget, name='create_budget'),
    path('detail_budget/<int:pk>/', detail_budget, name='detail_budget'),
    path('edit_budget/<int:pk>/', edit_budget, name='edit_budget'),
    path('delete_budget/<int:pk>/', delete_budget, name='delete_budget'),
    path('duplicate_budget/<int:pk>/', views.duplicate_budget, name='duplicate_budget'),
    path('export_budget/<int:pk>/', export_budget_report, name="export_budget_report"),
    path('create_sales_order/<int:budget_id>/', create_sales_order_from_budget, name='create_sales_order'),
    path('ajax/catalog-item-search/', catalog_item_search, name='catalog_item_search'),
    path('edit_new_budget/<int:pk>/', edit_budget_with_new_item, name='edit_budget_with_new_item'),

    # Catalog
    path('catalog/', views.catalog, name='budget_catalog'),
    path('catalog/new/', views.catalog_new, name='budget_catalog_new'),
    path('catalog/search/', views.catalog_search, name='budget_catalog_search'),
    path('catalog/edit/<int:catalog_id>/', views.catalog_edit, name='catalog_edit'),
    path('catalog/new/', views.catalog_new, name='budget_catalog_new'), 
    path('catalog/excel/', views.upload_excel, name='budget_catalog_excel'),
]
