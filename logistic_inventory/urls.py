from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='logistic_inventory_index')
]

htmxurlpatters = [
    # Brand
    path('brand/', views.brand, name='logistic_inventory_brand'),
    path('brand/edit/<int:brand_id>/', views.brand_edit, name='logistic_inventory_brand_edit'),
    path('brand/new/', views.brand_new, name='logistic_inventory_brand_new'),
    path('brand/search/', views.brand_search, name='logistic_inventory_brand_search'),
    # Item
    path('item/', views.item, name='logistic_inventory_item'),
    path('item/new/', views.item_new, name='logistic_inventory_item_new'),
    path('item/search/', views.item_search, name='logistic_inventory_item_search'),
    #path('item/new/allsubtype', views.item_search, name='logistic_inventory_item_all_subtypes'),
    path('item/edit/<int:item_id>/', views.item_edit, name='logistic_inventory_item_edit'),
    # Subtype
    path('subtype/', views.subtype, name='logistic_inventory_subtype'),
    path('subtype/edit/<int:subtype_id>/', views.subtype_edit, name='logistic_inventory_subtype_edit'),
    path('subtype/new/', views.subtype_new, name='logistic_inventory_subtype_new'),
    path('subtype/search/', views.subtype_search, name='logistic_inventory_subtype_search'),
    # Type
    path('type/', views.type, name='logistic_inventory_type'),
    path('type/edit/<int:type_id>/', views.type_edit, name='logistic_inventory_type_edit'),
    path('type/new/', views.type_new, name='logistic_inventory_type_new'),
    path('type/search/', views.type_search, name='logistic_inventory_type_search'),
    # Function
    path('item/getallsubtype/', views.get_all_subtypes, name='logistic_inventory_all_subtypes'),
]

urlpatterns += htmxurlpatters
