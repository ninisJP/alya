from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='logistic_inventory_index')
]

htmxurlpatters = [
    # Brand
    path('brand/', views.brand, name='logistic_inventory_brand'),
    path('brand/new/', views.brand_new, name='logistic_inventory_brand_new'),
    path('brand/search/', views.brand_search, name='logistic_inventory_brand_search'),
    # Item
    path('item/', views.item, name='logistic_inventory_item'),
    path('item/new/', views.item_new, name='logistic_inventory_item_new'),
    path('item/search/', views.item_search, name='logistic_inventory_item_search'),
    path('item/download/qr/all/', views.item_download_all_qr, name='logistic_inventory_item_download_all_qr'),
    # Subtype
    path('subtype/', views.subtype, name='logistic_inventory_subtype'),
    path('subtype/new/', views.subtype_new, name='logistic_inventory_subtype_new'),
    path('subtype/search/', views.subtype_search, name='logistic_inventory_subtype_search'),
    # Type
    path('type/', views.type, name='logistic_inventory_type'),
    path('type/new/', views.type_new, name='logistic_inventory_type_new'),
    path('type/search/', views.type_search, name='logistic_inventory_type_search'),
    # Function
    path('item/getallsubtype/', views.get_all_subtypes, name='logistic_inventory_all_subtypes'),
]

urlpatterns += htmxurlpatters
