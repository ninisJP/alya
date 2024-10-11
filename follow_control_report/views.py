from django.http import JsonResponse
from django.shortcuts import render, redirect
from datetime import date, datetime
import calendar

from .utils import get_daily_valuations_for_month


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
