from django.db.models import Max
from datetime import date, timedelta

from follow_control_card.models import Card, CardTaskOrder


def get_max_order(card) -> int:
    existing_tasks = CardTaskOrder.objects.filter(card=card)
    if not existing_tasks.exists():
        return 1
    else:
        current_max = existing_tasks.aggregate(max_order=Max('order'))['max_order']
        return current_max + 1


def create_monthly_cards_for_user(user):
    today = date.today()
    start_of_month = today.replace(day=1)
    next_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1)
                  if start_of_month.month != 12 else start_of_month.replace(year=start_of_month.year + 1, month=1, day=1))
    days_in_month = (next_month - start_of_month).days

    for day in range(days_in_month):
        card_date = start_of_month + timedelta(days=day)
        Card.objects.get_or_create(user=user, date=card_date)
