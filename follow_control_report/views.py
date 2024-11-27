from django.http import JsonResponse
from django.shortcuts import render, redirect
from datetime import date, datetime
import calendar
from follow_control_card.models import Card
from datetime import date as dt
from .utils import get_daily_valuations_for_month
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from datetime import date as dt


def valuations_view(request, year, month):
    today = date.today()
    if year != today.year or month != today.month:
        return redirect('valuations', year=today.year, month=today.month)
        
    raw_valuations = get_daily_valuations_for_month(year, month)
    
    _, num_days = calendar.monthrange(year, month)
    days = list(range(1, num_days + 1))
    
    valuations = []
    for user, days_valuations in raw_valuations.items():
        row = [user] + [days_valuations.get(day, '-') for day in days]
        valuations.append(row)

    return render(request, 'valuations_list.html', {
        'valuations': valuations,
        'days': days
    })

def daily_evaluation_cards(request):
    # Obtener la fecha desde los parámetros GET
    date = request.GET.get('date')

    # Si no se pasa una fecha, usar la fecha actual como predeterminada
    if not date:
        date = dt.today().strftime('%Y-%m-%d')

    # Filtrar las tarjetas por la fecha proporcionada, incluyendo las tareas asociadas
    cards = Card.objects.filter(date=date).prefetch_related('tasks')

    # Pasar las tarjetas y la fecha al template
    context = {
        'cards': cards,
        'selected_date': date,
    }
    return render(request, 'dailyvaluation/daily_evaluation_cards.html', context)
