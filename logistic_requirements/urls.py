from django.urls import path
from .views import RequirementOrderListView, RequirementOrderDetailView
from . import views

urlpatterns = [
    path('requirement-orders/', RequirementOrderListView.as_view(), name='requirement_order_list'),
    path('requirement-order/detail/<int:pk>/', RequirementOrderDetailView.as_view(), name='requirement_order_detail'),
    path('requirement-order/<int:pk>/', views.edit_requirement_order, name='requirement_order_edit'),
]
