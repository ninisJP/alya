from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.input_index, name='logistic_inventory_input_index'),
]
