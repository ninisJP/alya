from django.urls import path
from .views import valuations_view, daily_evaluation_cards
from . import views

urlpatterns = [
    path('valuations/<int:year>/<int:month>/', valuations_view, name='valuations'),
    path('daily-valuation/', daily_evaluation_cards, name='daily_evaluation_cards'),
    path('etiquetar-tareas/', views.label_tasks, name='label_tasks'),
   
]
