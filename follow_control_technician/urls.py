from django.urls import path
from . import views

urlpatterns = [
    path('informe-tecnicos/<int:mes>/<int:anio>/', views.TechniciansMonth.as_view(), name='technicians_month'),
    path('ver-tarjeta-tecnico/<int:card_id>/', views.view_technician_card, name='view_technician_card'),
    path('create-technician-card/<int:mes>/<int:anio>/', views.create_technician_card, name='create_technician_card'),
    path('delete-technician-card/<int:card_id>/', views.delete_technician_card, name='delete_technician_card'),
    path('technician-tasks/', views.technician_task, name='technician_task'),
    path('technician-task-state/<int:pk>/', views.technician_task_state, name='technician-task-state'),
    path('technician/calendar/', views.technician_calendar, name='technician_calendar'),
]

htmxurlpatters = [
    path('create-tasks/', views.create_technician_task, name='create-technician-tasks'),
    path('delete-task/<int:task_id>/', views.delete_technician_task, name='delete-technician-task'),
    path('edit-task/<int:task_id>/', views.edit_technician_task, name='edit-technician-task'), 
    path('add-task/<int:card_id>/', views.add_technician_task, name='add_technician_task'),
    path('delete_technician_card_task/<int:task_id>/', views.delete_technician_card_task, name='delete_technician_card_task'),
]

urlpatterns += htmxurlpatters
