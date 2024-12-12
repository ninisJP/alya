from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .utils import get_month_dates
from .forms import CardTaskForm
from follow_control_card.models import Card, CardTaskOrder
from follow_control_card.utils import get_max_order


def weekly_backlog(request, year=None, week=None):
    user = request.user

    # Obtener la fecha de hoy si no se proporciona año y semana
    if request.GET.get('year') and request.GET.get('week'):
        year = int(request.GET.get('year'))
        week = int(request.GET.get('week'))
    else:
        today = datetime.today()
        year, week, _ = today.isocalendar()

    # Calcular el rango de fechas para la semana dada
    start_of_week = datetime.strptime(f'{year}-W{week}-1', "%Y-W%W-%w").date()
    days_of_week = [(start_of_week + timedelta(days=i)) for i in range(7)]

    # Calcular la semana anterior y siguiente
    previous_week_date = start_of_week - timedelta(days=7)
    next_week_date = start_of_week + timedelta(days=7)
    previous_year, previous_week, _ = previous_week_date.isocalendar()
    next_year, next_week, _ = next_week_date.isocalendar()

    # Calcular la semana actual
    current_year, current_week, _ = datetime.today().isocalendar()

    # Filtrar por el usuario seleccionado
    selected_user_id = request.GET.get('user', None)
    if selected_user_id:
        selected_user = User.objects.get(id=selected_user_id)
    else:
        selected_user = user

    # Filtrar las Cards para la semana específica
    cards = Card.objects.filter(
        user=selected_user,
        date__range=(start_of_week, days_of_week[-1])
    )

    form = CardTaskForm(user=selected_user)
    all_users = User.objects.all()

    context = {
        'days_of_week': days_of_week,
        'year': year,
        'week': week,
        'previous_year': previous_year,
        'previous_week': previous_week,
        'next_year': next_year,
        'next_week': next_week,
        'current_year': current_year,
        'current_week': current_week,
        'cards': cards,
        'form': form,
        'all_users': all_users,
        'selected_user': selected_user,
    }
    return render(request, 'weekly_backlog.html', context)


def backlog(request, year=None, month=None):
    user = request.user

    if request.GET.get('year') and request.GET.get('month'):
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
    elif year is None or month is None:
        today = datetime.today()
        year = today.year
        month = today.month

    # Filtrar por el usuario seleccionado
    selected_user_id = request.GET.get('user', None)
    if selected_user_id:
        selected_user = User.objects.get(id=selected_user_id)
    else:
        selected_user = user

    month_data = get_month_dates(year, month)

    cards = Card.objects.filter(
        user=selected_user,
        date__range=(month_data['start_of_month'], month_data['end_of_month'])
    ).exclude(date__week_day=1)  # Exclude Sundays

    form = CardTaskForm(user=user)
    all_users = User.objects.all()

    context = {
        'nombre_mes': month_data['nombre_mes'],
        'anio': month_data['current_year'],
        'mes': month_data['current_month'],
        'cards': cards,
        'days_in_month': month_data['days_in_month'],
        'empty_days': month_data['empty_days'],
        'form': form,
        'months': month_data['months'],
        'years': month_data['years'],
        'all_users': all_users,
        'selected_user': selected_user,
    }
    return render(request, 'backlog.html', context)

def add_task(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)
    if request.method == 'POST':
        form = CardTaskForm(request.POST, user=request.user)
        if form.is_valid():
            tasks = form.cleaned_data['tasks']
            for task in tasks:
                max_order = get_max_order(card)
                CardTaskOrder.objects.create(card=card, task=task, order=max_order)
            card.update_card_values()
            return redirect('backlog_default')
    else:
        form = CardTaskForm(user=request.user)
    return render(request, 'backlog/modal_content.html', {'form': form, 'card': card})

def clear_tasks_from_card(request, card_id):
    card = get_object_or_404(Card, id=card_id, user=request.user)

    if request.method == 'POST':
        # Eliminar todas las relaciones de tareas con la Card
        card.tasks.clear()
        card.update_card_values()  # Actualizar valores de la Card después de eliminar tareas
        messages.success(request, "Todas las tareas han sido eliminadas de la tarjeta.")
        return redirect('backlog_default')

    return render(request, 'backlog/confirm_clear_tasks.html', {'card': card})


def replicate_tasks_to_new_card(source_card, target_card):
    """
    Replica las tareas de una Card a otra sin duplicarlas.

    :param source_card: Card desde donde se replicarán las tareas.
    :param target_card: Card a la que se copiarán las tareas.
    """
    # Asegúrate de que ambas Cards pertenecen al mismo usuario
    if source_card.user != target_card.user:
        raise ValueError("Las Cards deben pertenecer al mismo usuario.")

    # Usamos una transacción para asegurar la atomicidad
    with transaction.atomic():
        tasks_to_replicate = CardTaskOrder.objects.filter(card=source_card)
        for task_order in tasks_to_replicate:
            # Verificar si la tarea ya existe en la target_card
            if not CardTaskOrder.objects.filter(card=target_card, task=task_order.task).exists():
                CardTaskOrder.objects.create(
                    card=target_card,
                    task=task_order.task,
                    order=task_order.order,
                    state=False  # Asumimos que el estado se reinicia
                )

        # Actualizamos los valores de la nueva Card
        target_card.update_card_values()
        target_card.update_valuation()

    print(f"Tareas replicadas de {source_card} a {target_card} sin duplicaciones")

def replicate_last_week_tasks(request):
    user = request.user

    # Obtener la fecha de hoy y calcular el lunes de esta semana
    today = timezone.now().date()
    start_of_this_week = today - timedelta(days=today.weekday())

    # Calcular el lunes de la semana pasada
    start_of_last_week = start_of_this_week - timedelta(days=7)

    # Filtrar las Cards de la semana pasada
    last_week_cards = Card.objects.filter(
        user=user,
        date__range=(start_of_last_week, start_of_last_week + timedelta(days=6))
    )

    if not last_week_cards.exists():
        messages.error(request, "No se encontraron tarjetas para replicar de la semana pasada.")
        return redirect('backlog_default')

    # Crear las nuevas Cards para la semana actual
    for last_week_card in last_week_cards:
        new_card_date = last_week_card.date + timedelta(days=7)
        new_card, created = Card.objects.get_or_create(
            user=user,
            date=new_card_date,
            defaults={'valuation': 'D', 'total_time': 0.00}
        )

        # Replicar las tareas de la Card de la semana pasada a la nueva Card
        replicate_tasks_to_new_card(last_week_card, new_card)

    messages.success(request, "Tareas replicadas exitosamente para la semana actual.")
    return redirect('backlog_default')

# traspaso de tareas un día
def replicate_tasks_to_future_week(request):
    user = request.user

    # Obtener la fecha de hoy y calcular el lunes de esta semana
    today = timezone.now().date()
    start_of_this_week = today - timedelta(days=today.weekday())  # Lunes de esta semana

    # Filtrar las Cards de esta semana
    this_week_cards = Card.objects.filter(
        user=user,
        date__range=(start_of_this_week, start_of_this_week + timedelta(days=6))
    )

    if not this_week_cards.exists():
        messages.error(request, "No se encontraron tarjetas para esta semana.")
        return redirect('backlog_default')

    # Crear o buscar las nuevas Cards para el día siguiente (trasladar las tareas un día)
    for this_week_card in this_week_cards:
        # Calcular el día correspondiente en la semana objetivo (el día siguiente)
        target_day_card_date = this_week_card.date + timedelta(days=1)  # Mover un solo día hacia adelante

        # Asegurarse de que no se copien múltiples días. La fecha de destino debe ser solo un día.
        if target_day_card_date != this_week_card.date:  # Esto asegura que solo se mueva un día
            # Verificar si el día siguiente es un domingo (weekday() == 6 significa domingo)
            if target_day_card_date.weekday() == 6:  # Si es domingo, no replicar
                continue  # Saltar este día, no replicar tareas

            # Buscar o crear la nueva tarjeta para ese día
            target_day_card, created = Card.objects.get_or_create(
                user=user,
                date=target_day_card_date,
                defaults={'valuation': 'D', 'total_time': 0.00}
            )

            # Replicar las tareas de la Card de este día a la nueva Card del siguiente día
            replicate_tasks_to_new_card(this_week_card, target_day_card)

    messages.success(request, "Tareas replicadas exitosamente.")
    return redirect('backlog_default')

def replicate_tasks_to_previous_week_filling_gaps(request):
    user = request.user

    # Obtener la fecha de hoy y calcular el lunes de esta semana
    today = timezone.now().date()
    start_of_this_week = today - timedelta(days=today.weekday())

    # Inicializar la semana objetivo con la semana pasada
    start_of_target_week = start_of_this_week - timedelta(days=7)

    while True:
        # Filtrar las Cards de la semana objetivo
        target_week_cards = Card.objects.filter(
            user=user,
            date__range=(start_of_target_week, start_of_target_week + timedelta(days=6))
        )

        # Crear un diccionario para ver si cada día de la semana tiene tareas
        days_with_tasks = {start_of_target_week + timedelta(days=i): False for i in range(7)}
        for card in target_week_cards:
            if card.tasks.exists():
                days_with_tasks[card.date] = True

        # Si todos los días tienen tareas, pasar a la semana anterior
        if all(days_with_tasks.values()):
            start_of_target_week -= timedelta(days=7)
        else:
            # Si hay días vacíos, replicar solo en esos días
            break

    # Filtrar las Cards de esta semana
    this_week_cards = Card.objects.filter(
        user=user,
        date__range=(start_of_this_week, start_of_this_week + timedelta(days=6))
    )

    if not this_week_cards.exists():
        messages.error(request, "No se encontraron tarjetas para esta semana.")
        return redirect('backlog_default')

    # Replicar las tareas solo en los días vacíos de la semana objetivo
    for this_week_card in this_week_cards:
        target_card_date = this_week_card.date - (start_of_this_week - start_of_target_week)
        if not days_with_tasks[target_card_date]:
            target_card, created = Card.objects.get_or_create(
                user=user,
                date=target_card_date,
                defaults={'valuation': 'D', 'total_time': 0.00}
            )
            # Replicar las tareas de la Card de esta semana a la nueva Card de la semana objetivo
            replicate_tasks_to_new_card(this_week_card, target_card)

    messages.success(request, "Tareas replicadas exitosamente a la semana anterior.")
    return redirect('backlog_default')
