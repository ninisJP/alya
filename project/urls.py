from django.urls import path


from .views import project_index, ProjectSalesOrderListView

urlpatterns = [
    path('', project_index, name='project_index'),
    path('proyectos/', ProjectSalesOrderListView.as_view(), name='project_sales_order_list'),

]
