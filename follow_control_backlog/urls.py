from django.urls import path
from .views import backlog, add_task, replicate_last_week_tasks, replicate_tasks_to_future_week, weekly_backlog, replicate_tasks_to_previous_week_filling_gaps, clear_tasks_from_card

urlpatterns = [
    path('weekly-backlog/', weekly_backlog, name='weekly_backlog'),
    path('backlog/', backlog, name='backlog_default'),
    path('backlog/<int:year>/<int:month>/', backlog, name='backlog'),
    path('backlog/add_task/<int:card_id>/', add_task, name='add_task'),
    path('clear-tasks/<int:card_id>/', clear_tasks_from_card, name='clear_tasks_from_card'),
    path('replicate-last-week-tasks/', replicate_last_week_tasks, name='replicate_last_week_tasks'),
    path('replicate-this-week-tasks-next-week/', replicate_tasks_to_future_week, name='replicate_this_week_tasks_to_next_week'),
    path('replicate-tasks-to-future-week/', replicate_tasks_to_previous_week_filling_gaps, name='replicate_tasks_to_previous_week'),
]
