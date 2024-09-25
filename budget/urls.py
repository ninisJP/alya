from django.urls import path
from .views import index_budget, create_budget, detail_budget, edit_budget, delete_budget, catalog, export_budget_report
from . import views

urlpatterns = [
    path('', index_budget, name='index_budget'),
    path('create_budget/', create_budget, name='create_budget'),
    path('detail_budget/<int:pk>/', detail_budget, name='detail_budget'),
    path('edit_budget/<int:pk>/', edit_budget, name='edit_budget'),
    path('delete_budget/<int:pk>/', delete_budget, name='delete_budget'),
    path('duplicate_budget/<int:pk>/', views.duplicate_budget, name='duplicate_budget'),
    path('export_budget/<int:pk>/', export_budget_report, name="export_budget_report"),
   
    # Catalog
    path('catalog/', views.catalog, name='budget_catalog'),
    path('catalog/new/', views.catalog_new, name='budget_catalog_new'),
    path('catalog/search/', views.catalog_search, name='budget_catalog_search'),
    path('catalog/edit/<int:catalog_id>/', views.catalog_edit, name='catalog_edit'),
]
