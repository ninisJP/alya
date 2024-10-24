from django.urls import path
from .views import RequirementOrderListView,RequirementOrderApprovedListView,  requirement_order_detail_view, update_requirement_order_items, requirement_order_detail_partial
from . import views

urlpatterns = [
    path('requirement-orders/', RequirementOrderListView.as_view(), name='requirement_order_list'),
    path('requirement-orders-approved/', RequirementOrderApprovedListView.as_view(), name='requirement_order_approved_list'),
    path('requirement-order-detail-partial/<int:pk>/', requirement_order_detail_partial, name='requirement_order_detail_partial'),
    path('requirement-order/detail/<int:pk>/', requirement_order_detail_view, name='requirement_order_detail'),
    path('ajax/load-suppliers/', views.ajax_load_suppliers, name='ajax_load_suppliers'),
    path('requirement-order/update-items/<int:pk>/', update_requirement_order_items, name='update_requirement_order_items'),
    path('requirement-order/create-purchase-order/<int:pk>/', views.create_purchase_order, name='create_purchase_order'),
]
