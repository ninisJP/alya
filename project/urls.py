from django.urls import path


from .views import project_index, ProjectSalesOrderListView,sales_order_detail, sales_order_partial_view, purchase_order_partial_view, requirement_order_partial_view

urlpatterns = [
    path('', project_index, name='project_index'),
    path('proyectos/', ProjectSalesOrderListView.as_view(), name='project_sales_order_list'),
    path('sales_order/<int:order_id>/', sales_order_detail, name='sales_order_detail'),
    path('sales-order-partial/<int:order_id>/', sales_order_partial_view, name='sales_order_partial'),
    path('purchase-order-partial/<int:order_id>/', purchase_order_partial_view, name='purchase_order_partial'),
    path('requirement-order-partial/<int:order_id>/', requirement_order_partial_view, name='requirement_order_partial'),




]
