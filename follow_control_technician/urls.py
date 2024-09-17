from django.urls import path

from .views import technician_task_state, TechniciansMonth, create_technician_card, view_technician_card, edit_technician_card, technician_task, create_technician_task, delete_technician_task, edit_technician_task, delete_technician_card

urlpatterns = [
    path('informe-tecnicos/<int:mes>/<int:anio>/', TechniciansMonth.as_view(), name='technicians_month'),
    path('ver-tarjeta-tecnico/<int:tecnico_id>/<int:dia>/<int:mes>/<int:anio>/', view_technician_card, name='view_technician_card'),
    path('create-technician-card/<int:mes>/<int:anio>/', create_technician_card, name='create_technician_card'),
    path('edit-technician-card/<int:card_id>/<int:mes>/<int:anio>/', edit_technician_card, name='edit_technician_card'),
    path('delete-technician-card/<int:card_id>/', delete_technician_card, name='delete_technician_card'),
    path('technician-tasks/', technician_task, name='technician_task'),
    path('technician-task-state/<int:pk>/', technician_task_state, name='technician-task-state'),
]

htmxurlpatters = [
     #tasks urls
    path('create-tasks/', create_technician_task, name='create-technician-tasks' ),
    path('delete-task/<int:task_id>/', delete_technician_task, name='delete-technician-task'),
    path('edit-task/<int:task_id>/', edit_technician_task, name='edit-technician-task'),  # Asegúrate de que el nombre sea correcto

    
]

urlpatterns += htmxurlpatters