from django.urls import path
from .views import valuations_view, daily_evaluation_cards, get_card_details

urlpatterns = [
    path('valuations/<int:year>/<int:month>/', valuations_view, name='valuations'),
    path('daily-valuation/', daily_evaluation_cards, name='daily_evaluation_cards'),
    path('get_card_details/<int:card_id>/', get_card_details, name='get_card_details'),

]
