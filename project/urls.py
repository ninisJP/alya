from django.urls import path


from .views import project_index, ProjectSalesOrderListView,sales_order_detail

urlpatterns = [
    path('', project_index, name='project_index'),
    path('proyectos/', ProjectSalesOrderListView.as_view(), name='project_sales_order_list'),
    path('sales_order/<int:order_id>/', sales_order_detail, name='sales_order_detail'),


]
