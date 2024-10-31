from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.input_index, name='logistic_inventory_inputnewitem_index'),
    path('new/<int:purchase_pk>/', views.input_new, name='logistic_inventory_inputnewitem_new'),
    path('new/<int:purchase_pk>/search/', views.input_new_search, name='logistic_inventory_inputnewitem_new_search'),
    path('new/<int:purchase_item_pk>/item', views.input_new_item, name='logistic_inventory_inputnewitem_new_item'),
]
