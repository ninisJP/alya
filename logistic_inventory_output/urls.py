from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.output_index, name='logistic_inventory_output_index'),
    path('new/salesorder/', views.output_new_salesorder, name='logistic_inventory_output_new_salesorder_search'),
    path('new/<int:saleorder_id>/', views.output_new, name='logistic_inventory_output_new'),
    path('new/<int:output_pk>/list/', views.output_new_list, name='logistic_inventory_output_new_list'),
    path('new/<int:output_pk>/<int:requirement_item_pk>/<int:logistic_item_pk>/', views.output_new_item, name='logistic_inventory_output_new_item'),
    path('see/<int:output_pk>/', views.output_see, name='logistic_inventory_output_see'),
]
