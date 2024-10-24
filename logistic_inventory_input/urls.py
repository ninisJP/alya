from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.input_index, name='logistic_inventory_input_index'),
    path('new/<int:output_pk>/', views.input_new, name='logistic_inventory_input_new'),
]
