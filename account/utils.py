from datetime import date, timedelta
from cards.models import Cards

def create_monthly_cards_for_user(user):
    today = date.today()
    start_of_month = today.replace(day=1)
    next_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) 
                  if start_of_month.month != 12 else start_of_month.replace(year=start_of_month.year + 1, month=1, day=1))
    days_in_month = (next_month - start_of_month).days

    for day in range(days_in_month):
        card_date = start_of_month + timedelta(days=day)
        Cards.objects.get_or_create(user=user, date=card_date)

