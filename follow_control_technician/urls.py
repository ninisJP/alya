from django.urls import path

from .views import TechniciansMonth, create_technician, create_technician_card, create_technician_task, view_technician_card

urlpatterns = [
    # URL para el informe de tarjetas de técnicos del mes
    path('informe-tecnicos/<int:mes>/<int:anio>/', TechniciansMonth.as_view(), name='technicians_month'),
    path('ver-tarjeta-tecnico/<int:tecnico_id>/<int:dia>/<int:mes>/<int:anio>/', view_technician_card, name='view_technician_card'),
    path('crear-tecnico/', create_technician, name='create_technician'),
    path('crear-tarea-tecnico/', create_technician_task, name='create_technician_task'),
    path('crear-tarjeta-tecnico/', create_technician_card, name='create_technician_card'),
    path('crear-tarjeta-tecnico/<int:tecnico_id>/<int:dia>/<int:mes>/<int:anio>/', create_technician_card, name='create_technician_card'),
]
