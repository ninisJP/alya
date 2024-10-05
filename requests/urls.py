from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_requests, name='index_requests'),
    path('crear-pedido/<int:order_id>/', views.create_requests, name='create_requests'),
    path('mis-pediddos/', views.my_requests, name='my_requests'),
    path('mi-pedido/<int:pk>/', views.MyRequestDetail.as_view(), name='my_request_detail'),
]
