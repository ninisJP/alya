from django.urls import path

from .views import TechniciansMonth, create_technician_card, view_technician_card, add_task_form, technician_task, create_technician_task, delete_technician_task, edit_technician_task

urlpatterns = [
    path('informe-tecnicos/<int:mes>/<int:anio>/', TechniciansMonth.as_view(), name='technicians_month'),
    path('ver-tarjeta-tecnico/<int:tecnico_id>/<int:dia>/<int:mes>/<int:anio>/', view_technician_card, name='view_technician_card'),
    path('crear-tarjeta-tecnico/', create_technician_card, name='create_technician_card'),
    path('add-task-form/', add_task_form, name='add_task_form'),
    path('technician-tasks/', technician_task, name='technician_task')
]

htmxurlpatters = [
     #tasks urls
    path('create-tasks/', create_technician_task, name='create-technician-tasks' ),
    path('delete-task/<int:task_id>/', delete_technician_task, name='delete-technician-task'),
    path('edit-task/<int:task_id>/', edit_technician_task, name='edit-technician-task'),  # Asegúrate de que el nombre sea correcto

    
]

urlpatterns += htmxurlpatters