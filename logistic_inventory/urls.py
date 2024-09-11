from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='logistic_inventory_index')
]

htmxurlpatters = [
    path('item/', views.item, name='logistic_inventory_item' ),
    path('type/', views.type, name='logistic_inventory_type' ),
    path('subtype/', views.subtype, name='logistic_inventory_subtype' ),
    path('brand/', views.brand, name='logistic_inventory_brand' ),
    path('brand/new', views.brand_new, name='logistic_inventory_brand_new' ),
]

urlpatterns += htmxurlpatters
