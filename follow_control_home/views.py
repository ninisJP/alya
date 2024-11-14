from django.shortcuts import render
from django.utils.timezone import now
from follow_control_card.models import Card

from django.utils.timezone import now
import calendar
from collections import defaultdict

def HomeCC(request):
    if not request.user.is_authenticated:
        return render(request, 'follow_control_home.html', {'cards': []})

    today = now()
    current_year, current_month = today.year, today.month
    _, days_in_month = calendar.monthrange(current_year, current_month)

    # Consulta para obtener todas las `cards` del usuario en el rango del mes actual
    start_of_month = today.replace(day=1)
    end_of_month = start_of_month.replace(day=days_in_month)

    cards = Card.objects.filter(
        user=request.user,
        date__range=(start_of_month, end_of_month)
    ).exclude(date__week_day=1)

    # Agrupa las cards por día para pasarlas a FullCalendar
    cards_by_date = defaultdict(list)
    for card in cards:
        cards_by_date[card.date].append(card)

    # Obtener el mes y año en formato amigable
    current_month_text = today.strftime('%B %Y')

    return render(request, 'follow_control_home.html', {
        'cards_by_date': cards_by_date,
        'current_month': current_month_text,
    })
