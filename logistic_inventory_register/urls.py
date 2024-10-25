from django.urls import path

from . import views

urlpatterns = [
    path('index/', views.index, name='logistic_inventory_register_index'),
]
