from django.http import JsonResponse
from django.shortcuts import render, redirect
from datetime import date, datetime
import calendar
from follow_control_card.models import Card, Task, TaskExecution
from datetime import date as dt
from .utils import get_daily_valuations_for_month
from django.shortcuts import get_object_or_404
from django.db.models import Count
from datetime import timedelta
import pandas as pd
from django.db.models import Q
from follow_control_card.forms import * 
from django.db.models import Count
from employee.models import Supervisor
from datetime import date as dt

FREQUENCY_THRESHOLD = 5  # Si la tarea se ejecuta más de 5 veces en el mes, es rutinaria


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
    date = request.GET.get('date')

    if not date:
        date = dt.today().strftime('%Y-%m-%d')

    # Obtener los usuarios que son supervisores
    supervisors = Supervisor.objects.filter(status="active")

    # Filtrar las tarjetas (cards) que corresponden a los supervisores
    # Aquí asumo que quieres filtrar por los supervisores específicos
    user_ids = [supervisor.user.id for supervisor in supervisors]

    # Filtrar tarjetas de los usuarios que son supervisores y la fecha seleccionada
    cards = Card.objects.filter(date=date, user__id__in=user_ids).annotate(task_count=Count('cardtaskorder'))

    context = {
        'cards': cards,
        'selected_date': date,
    }
    return render(request, 'dailyvaluation/daily_evaluation_cards.html', context)


def daily_evaluation_search(request):
    query = request.GET.get('q', '')  
    
    today = date.today() # Obtener la fecha de hoy

    if query:
        cards = Card.objects.filter(
            Q(user__username__icontains=query) & Q(date=today)  # Filtrar por nombre de usuario y fecha de hoy
        ).order_by('-id')
    else:
        cards = Card.objects.filter(date=today).order_by('-id')  # Solo mostrar tarjetas del día de hoy

    context = {'cards': cards, 'form': CardForm()}
    return render(request, 'dailyvaluation/daily_evaluation_card_list.html', context)


def label_tasks(request):
    if request.method == 'POST':
        tasks = Task.objects.all()  

        results = []
        for task in tasks:
            label = label_task_as_routine(task)
            task.label = label 
            task.save() 
            results.append({'task': task.verb, 'label': label})

        return render(request, 'label_results.html', {'results': results})

    return render(request, 'label_tasks.html')

# Función para determinar si una tarea es rutinaria o no
def label_task_as_routine(task):
    # Contamos cuántas veces se ejecutó la tarea en los últimos 30 días
    executions_in_last_30_days = TaskExecution.objects.filter(
        task=task, 
        executed_at__gte=pd.to_datetime('today') - timedelta(days=30)
    ).count()

    # Si la tarea se ejecutó más veces que el umbral, la marcamos como rutinaria
    return 'rutinaria' if executions_in_last_30_days >= FREQUENCY_THRESHOLD else 'no_rutinaria'
