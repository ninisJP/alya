from django.urls import path

from .views import DailyCardList, add_daily_task, delete_daily_task, search_task, add_task_to_card, sort_tasks, tasks, create_tasks, delete_task, edit_task, toggle_task_state , task_search

urlpatterns = [
    path('daily_card/<int:pk>/', DailyCardList.as_view(), name='daily_card'),
    path('tasks/', tasks, name='tasks'),
    path('tasks/search/task',task_search, name='task_search'),

    # Otras rutas...
]

htmxurlpatters = [
    path('add-daily-task/', add_daily_task, name='add-daily-task'),
    path('delete-daily-task/<int:pk>/', delete_daily_task, name='delete-daily-task'),
    path('search-task/', search_task, name='search-task'),
    path('add-task-to-card/<int:task_id>/', add_task_to_card, name='add-task-to-card'),
    path('sort-tasks/', sort_tasks, name='sort-tasks'),
    path('toggle-task-state/<int:pk>/', toggle_task_state, name='toggle-task-state'),

    #tasks urls
    path('create-tasks/', create_tasks, name='create-tasks' ),
    path('delete-task/<int:task_id>/', delete_task, name='delete-task'),
    path('edit-task/<int:task_id>/', edit_task, name='edit-task'),
]

urlpatterns += htmxurlpatters
