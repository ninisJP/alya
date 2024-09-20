from django.urls import path
from .views import RequirementOrderListView, create_requirement_order, RequirementOrderDetailView

urlpatterns = [
    path('requirement-orders/', RequirementOrderListView.as_view(), name='requirement_order_list'),
    path('requirement-order/create/', create_requirement_order, name='create_requirement_order'),
    path('requirement-order/<int:pk>/', RequirementOrderDetailView.as_view(), name='requirement_order_detail'),

]
