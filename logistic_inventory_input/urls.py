from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.input_index, name='logistic_inventory_input_index'),
    path('new/<int:output_pk>/', views.input_new, name='logistic_inventory_input_new'),
    path('new/<int:output_pk>/search/', views.input_new_search, name='logistic_inventory_input_new_search'),
    path('new/item/<int:outputitem_pk>/', views.input_new_item, name='logistic_inventory_input_new_item'),
]
