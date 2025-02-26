# See LICENSE file for copyright and license details.
"""
Request urls
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_requests, name='index_requests'),
    path(
        'crear-pedido/<int:order_id>/',
        views.create_requests,
        name='create_requests'
        ),
    path(
        'crear-pedido-prepoblado/<int:order_id>/',
        views.create_prepopulated_request,
        name='create_prepopulated_request'
        ),
    path(
        'mis-pedidos/',
        views.my_requests,
        name='my_requests'
        ),
    path(
        'mi-pedido/<int:pk>/',
        views.MyRequestDetail.as_view(),
        name='my_request_detail'
        ),
    path(
        'nuevo-pedido/<int:pk>/',
        views.request_sales_order,
        name='requests_plus'
        ),
    path(
        'ajax/load-suppliers/',
        views.ajax_load_suppliers,
        name='ajax_load_suppliers'
        ),
    path(
        'requirement_order_preview/',
        views.requirement_order_preview,
        name='requirement_order_preview'
        ),
    path(
        'exportar/orden-requerimiento/<int:order_id>/',
        views.export_requirement_order,
        name='export_requirement_order'
        ),
    path(
        'total-requests/',
        views.total_requests,
        name='total_requests'
        ),
    path(
        'sales_order/<int:sales_order_id>/requirements/',
        views.requirement_orders_view,
        name='requirement_orders_view'
        ),
]

htmxpatterms = [
    path(
        'delete_order/<int:order_id>/',
        views.delete_order,
        name='delete_order'),
    path(
        'create-requirement-order/<int:order_id>/',
        views.create_requirement_order,
        name='create_requirement_order'
        ),
    path(
        'delete-item/<int:item_id>/',
        views.delete_requirement_order_item,
        name='delete_requirement_order_item'
        ),

]

urlpatterns = urlpatterns + htmxpatterms
