from django.urls import path

from .views import TechniciansMonth, create_technician_card, view_technician_card, add_task_form

urlpatterns = [
    path('informe-tecnicos/<int:mes>/<int:anio>/', TechniciansMonth.as_view(), name='technicians_month'),
    path('ver-tarjeta-tecnico/<int:tecnico_id>/<int:dia>/<int:mes>/<int:anio>/', view_technician_card, name='view_technician_card'),
    path('crear-tarjeta-tecnico/', create_technician_card, name='create_technician_card'),
    path('add-task-form/', add_task_form, name='add_task_form'),
]
