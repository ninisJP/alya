from django.db.models import Q
from datetime import datetime

from django.urls import reverse

from follow_control_card.models import Card

def get_daily_valuations_for_month(year, month):
    print(f"get_daily_valuations_for_month funcionando correctamente!!")
    start_date = datetime(year, month, 1)
    end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    cards = Card.objects.filter(date__range=(start_date, end_date)).order_by('date')

    valuations = {}
    for card in cards:
        user = card.user.username
        day = card.date.day
        if user not in valuations:
            valuations[user] = {}
        if card.total_time > 0:
            link = reverse('daily_card', kwargs={'pk': card.id})
            valuations[user][day] = f'<a href="{link}">{card.valuation}</a>'
        else:
            valuations[user][day] = '-'

    return valuations
