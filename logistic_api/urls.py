# urls.py
from django.urls import path
from .views import requirement_order_list_view, get_requirement_order_items_view, edit_requirement_order_item_view

urlpatterns = [
    path('', requirement_order_list_view, name='requirement-order-list'),
    path('orders/<str:order_number>/items/', get_requirement_order_items_view, name='order-items'),
    path('orders/items/<int:item_id>/edit/', edit_requirement_order_item_view, name='edit-order-item'),
]
