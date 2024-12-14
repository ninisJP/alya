from django.db.models.query import QuerySet
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic.list import ListView
from datetime import datetime
from typing import Any
from accounting_order_sales.models import SalesOrder
from .forms import TaskForm
from .models import Card, Task, CardTaskOrder
from .utils import get_max_order
from django.db.models import Q
from django.utils import timezone



class DailyCardList(ListView):
    template_name = 'daily_card.html'
    model = Card
    context_object_name = 'cards'

    def get_queryset(self):
        user = self.request.user
        card_id = self.kwargs.get('pk')
        return Card.objects.filter(user=user, id=card_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card = self.get_queryset().first()

        if card:
            tasks_ordered = CardTaskOrder.objects.filter(card=card).order_by('order').select_related('task')
            context['daily_tasks'] = tasks_ordered
            context['card_id'] = card.id
            self.request.session['current_card_id'] = card.id
        else:
            context['daily_tasks'] = []
            context['card_id'] = None
            self.request.session['current_card_id'] = None

        # Obtener todas las SalesOrders o filtrarlas según sea necesario
        sale_orders = SalesOrder.objects.all()
        context['sale_orders'] = sale_orders  # Pasar las SalesOrders al contexto

        return context

from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.utils import timezone

def add_daily_task(request):
    """
    Función que agrega tareas a una tarjeta en función de la frecuencia seleccionada
    y las asocia con el calendario (fecha).
    """
    user = request.user
    verb = request.POST.get('taskname', '')
    object_ = request.POST.get('object', '')
    sale_order_id = request.POST.get('sale_order', '')
    measurement = request.POST.get('measurement', 'minutos')
    task_time = request.POST.get('task_time', None)
    card_id = request.POST.get('card_id')
    frecuency = request.POST.get('frecuency', 'UNA VEZ')

    # Asegurarse de que la tarjeta esté presente
    if not card_id:
        return render(request, 'partials/daily-task-list.html', {'error': 'Card ID is required'})

    card = get_object_or_404(Card, id=card_id, user=user)

    # Obtener la instancia de SalesOrder basada en sale_order_id
    sale_order = get_object_or_404(SalesOrder, id=sale_order_id)

    # Crear la nueva tarea con la frecuencia seleccionada
    with transaction.atomic():  # Asegurarse de que todo se guarde correctamente
        if frecuency == 'UNA VEZ':
            # Solo se crea la tarea una vez en el día de la tarjeta
            task = Task.objects.create(
                verb=verb,
                object=object_,
                sale_order=sale_order,
                measurement=measurement,
                task_time=task_time,
                user=user,
                frecuency=frecuency,
            )

            # Asociar la tarea con la tarjeta
            CardTaskOrder.objects.create(task=task, card=card, order=1)  # Puedes ajustar el orden si es necesario

            print(f"Tarea de una vez creada para el {card.date}")

        elif frecuency == 'SEMANAL':
            # Crear tarea semanal para el mismo día de la semana en el próximo ciclo
            task = Task.objects.create(
                verb=verb,
                object=object_,
                sale_order=sale_order,
                measurement=measurement,
                task_time=task_time,
                user=user,
                frecuency=frecuency,
            )

            # Calcular el próximo día específico de la semana (usando el mismo día de la semana de la tarjeta)
            today = timezone.now()
            days_until_next_week = 7 - today.weekday()  # Esto da el número de días hasta el próximo lunes
            next_week_date = today + timedelta(days=days_until_next_week)

            # Asociar la tarea con la tarjeta para la próxima semana
            CardTaskOrder.objects.create(task=task, card=card, order=1)  # Puedes ajustar el orden

            print(f"Tarea semanal programada para el {next_week_date.strftime('%Y-%m-%d')}")

        elif frecuency == 'DIARIO':
            # Crear tareas diarias para los próximos 7 días a partir de la `card.date`
            task = Task.objects.create(
                verb=verb,
                object=object_,
                sale_order=sale_order,
                measurement=measurement,
                task_time=task_time,
                user=user,
                frecuency=frecuency,
            )

            # Crear tareas diarias para los próximos 7 días a partir de la `card.date`
            for i in range(7):  # Crear tareas para cada día de la semana (7 días)
                next_day = card.date + timedelta(days=i)  # Sumar el número de días a partir de la fecha de la tarjeta
                
                # Convertir la fecha naive a aware con la zona horaria activa
                next_day_aware = timezone.make_aware(datetime.combine(next_day, datetime.min.time()))
                
                # Asociar la tarea con la tarjeta y con la fecha calculada
                CardTaskOrder.objects.create(
                    task=task, 
                    card=card, 
                    order=i+1,  # El orden puede ser ajustado si es necesario
                    executed_at=next_day_aware  # Establecer la fecha específica para la tarea
                )

                print(f"Tarea diaria programada para el {next_day_aware.strftime('%Y-%m-%d')}")

        # Actualizar los valores de la tarjeta (tiempo total, eficiencia, etc.)
        card.calculate_start_times()
        card.update_card_values()
        card.update_valuation()

    return render(request, 'partials/daily-task-list.html', {'daily_tasks': card.cardtaskorder_set.all(), 'card_id': card.id})



@require_http_methods(['DELETE'])
def delete_daily_task(request, pk):
    print(f"delete_daily_task: pk={pk}")  # Depuración
    task_order = get_object_or_404(CardTaskOrder, pk=pk)
    task = task_order.task
    card = task_order.card

    # Eliminar la relación en la tabla intermedia
    task_order.delete()

    # Obtener las tareas restantes para la tarjeta
    tasks_ordered = CardTaskOrder.objects.filter(card=card).order_by('order').select_related('task')
    daily_tasks = tasks_ordered

    return render(request, 'partials/daily-task-list.html', {'daily_tasks': daily_tasks, 'card_id': card.id})

def search_task(request):
    search_text = request.POST.get('search', '').strip()  # Elimina espacios innecesarios
    card_id = request.POST.get('card_id')

    if not card_id:
        card_id = request.session.get('current_card_id')  # Intenta obtener de la sesión
        if not card_id:
            # Manejar la falta de Card ID
            return JsonResponse({'error': 'Card ID is required'}, status=400)

    # Busca en `verb` y `object`
    results = Task.objects.filter(
        Q(verb__icontains=search_text) | Q(object__icontains=search_text),
        user=request.user
    )

    return render(request, 'partials/search-results.html', {'results': results, 'card_id': card_id})

def add_task_to_card(request, task_id):
    card_id = request.POST.get('card_id')
    if not card_id:
        return JsonResponse({'error': 'Card ID is required'}, status=400)


    card = get_object_or_404(Card, id=card_id, user=request.user)
    task = get_object_or_404(Task, id=task_id, user=request.user)

    # Verificar si la tarea ya está asociada a la tarjeta
    if CardTaskOrder.objects.filter(card=card, task=task).exists():
        return JsonResponse({'error': 'Task already added to this card'}, status=400)

    # Obtener el orden máximo actual y sumar 1 para la nueva tarea
    max_order = get_max_order(card)
    CardTaskOrder.objects.create(card=card, task=task, order=max_order)

    # Obtener las tareas ordenadas
    tasks_ordered = CardTaskOrder.objects.filter(card=card).order_by('order').select_related('task')
    daily_tasks = tasks_ordered  # Aquí no extraemos los tasks, sino que mantenemos los objetos CardTaskOrder

    return render(request, 'partials/daily-task-list.html', {'daily_tasks': daily_tasks, 'card_id': card.id})


@require_POST
def sort_tasks(request):
    task_pks_order = request.POST.getlist('task_order')
    card_id = request.session.get('current_card_id')

    if not card_id:
        return JsonResponse({'error': 'Card ID is required'}, status=400)

    tasks = []
    for idx, task_pk in enumerate(task_pks_order, start=1):
        task_order = get_object_or_404(CardTaskOrder, pk=task_pk, card_id=card_id)
        task_order.order = idx
        task_order.save()
        tasks.append(task_order)

    return render(request, 'partials/daily-task-list.html', {'daily_tasks': tasks, 'card_id': card_id})

@require_http_methods(["PATCH"])
def toggle_task_state(request, pk):
    """La función alterna el estado de una tarea (completada o no completada)"""
    task_order = get_object_or_404(CardTaskOrder, pk=pk, card__user=request.user)
    task_order.state = not task_order.state

    # Registrar la fecha de ejecución si se marca como completada
    task_order.executed_at = timezone.now() if task_order.state else None
    task_order.save()

    # Actualizar la valoración de la Card
    card = task_order.card
    card.update_valuation()
    print(task_order.executed_at)

    return HttpResponse(status=204)



# Iniciamos vista y metodos HTMX para tareas
def tasks(request):
    user_tasks = Task.objects.filter(user=request.user)
    context = {'form': TaskForm(), 'tasks': user_tasks}
    return render(request, 'tasks/task.html', context)

def task_search(request):
    query = request.GET.get('q', '')  # Obtener la consulta de búsqueda desde el request

    # Si hay una búsqueda, filtrar las órdenes de venta basadas en la consulta
    if query:
        tasks = Task.objects.filter(
            Q(verb__icontains=query) | 
            Q(object__icontains=query) | 
            Q(sale_order__detail__icontains=query) | 
            Q(measurement__icontains=query) | 
            Q(task_time__icontains=query)
            ).order_by('-id')
    else:
        tasks = Task.objects.all().order_by('-id')  # Mostrar todas las órdenes de venta si no hay búsqueda

    context = {'tasks': tasks , 'form': TaskForm()}
    # Devolver solo el fragmento de la lista
    return render(request, 'partials/task-list.html', context)


def create_tasks(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            user_tasks = Task.objects.filter(user=request.user)
            context = {'tasks': user_tasks}
            return render(request, 'partials/task-list.html', context)
    else:
        form = TaskForm()

    return render(request, 'partials/task-form.html', {'form': form})

def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'GET':
        form = TaskForm(instance=task)
        return render(request, 'partials/edit-task-form.html', {'form': form, 'task': task})
    elif request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            user_tasks = Task.objects.filter(user=request.user)
            return render(request, 'partials/task-list.html', {'tasks': user_tasks})
    return HttpResponse(status=405)

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'DELETE':
        task.delete()
        return render(request, 'partials/task-list.html')
    return HttpResponse(status=405)
