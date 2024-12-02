from django.urls import path
from .views import update_approved_items, RequirementOrderListView,requirement_order_approved_list,  requirement_order_detail_view, update_requirement_order_items, requirement_order_detail_partial, search_requirement_order_list_view
from . import views

urlpatterns = [
    path('requirement-orders/', RequirementOrderListView.as_view(), name='requirement_order_list'),
    path('requirement-orders/search/', search_requirement_order_list_view, name='requirement-order-search'),  # URL para la búsqueda
    path('requirement-orders-approved/', requirement_order_approved_list, name='requirement_order_approved_list'),
    path('requirement-order-detail-partial/<int:pk>/', requirement_order_detail_partial, name='requirement_order_detail_partial'),
    path('requirement-order/detail/<int:pk>/', requirement_order_detail_view, name='requirement_order_detail'),
    path('ajax/load-suppliers/', views.ajax_load_suppliers, name='ajax_load_suppliers'),
    path('export_order/<int:pk>/', views.export_order_to_excel, name='export_order_to_excel'),
]

htmxurlpatters = [
    path('requirement-order/update-items/', update_approved_items, name='update_approved_items'),
    path('requirement-order/update-items/<int:pk>/', update_requirement_order_items, name='update_requirement_order_items'),
    path('requirement-order/create-purchase-order/<int:pk>/', views.create_purchase_order, name='create_purchase_order'),
]

urlpatterns += htmxurlpatters
