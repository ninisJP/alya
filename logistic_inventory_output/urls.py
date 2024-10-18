from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.output_list, name='logistic_inventory_output_list'),
    path('new/', views.output_new, name='logistic_inventory_output_new'),
    path('see/<int:output_id>', views.output_see, name='logistic_inventory_output_see'),
]
