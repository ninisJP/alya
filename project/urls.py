from django.urls import path
from .views import project_index, ProjectSalesOrderListView,sales_order_detail, sales_order_partial_view, purchase_order_partial_view, requirement_order_partial_view
from .project_plus_views import project_order_plus
from . import views

urlpatterns = [
    path('', project_index, name='project_index'),
    path('proyectos/', ProjectSalesOrderListView.as_view(), name='project_sales_order_list'),
    path('sales_order/<int:order_id>/', sales_order_detail, name='sales_order_detail'),
    path('sales-order-partial/<int:order_id>/', sales_order_partial_view, name='sales_order_partial'),
    path('purchase-order-partial/<int:order_id>/', purchase_order_partial_view, name='purchase_order_partial'),
    path('requirement-order-partial/<int:order_id>/', requirement_order_partial_view, name='requirement_order_partial'),
    path('input-guide-partial/<int:order_id>/', views.input_guide_partial_view, name='project_detail_guide_input'),
    path('saleorder-input-guide-partial/<int:order_id>/', views.saleorder_input_guide_partial_view, name='project_detail_guide_input_saleorder'),
    path('output-guide-partial/<int:order_id>/', views.output_guide_partial_view, name='project_detail_guide_output'),
    path('diagram_project_orders/<int:order_id>/', views.diagram_project_orders, name='diagram_project_orders'),

    # project plus
    path('project_order/<int:order_id>/', project_order_plus, name='project_order_plus'),
]

