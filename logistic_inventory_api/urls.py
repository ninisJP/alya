from django.urls import path

from . import views

urlpatterns = [
    path('get/list/', views.get_list, name='logistic_inventory_api_get_list'),
    path('item/new/', views.item_new, name='logistic_inventory_api_item_new'),
    path('item/get/', views.item_get, name='logistic_inventory_api_item_get'),
]
