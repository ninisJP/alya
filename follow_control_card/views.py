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

def add_daily_task(request):
    user = request.user
    verb = request.POST.get('taskname', '')
    object_ = request.POST.get('object', '')
    sale_order_id = request.POST.get('sale_order', '')  # Asegúrate de que el name en el formulario es "sale_order"
    measurement = request.POST.get('measurement', 'minutos')
    task_time = request.POST.get('task_time', None)
    card_id = request.POST.get('card_id')

    if not card_id:
        return render(request, 'partials/daily-task-list.html', {'error': 'Card ID is required'})

    card = get_object_or_404(Card, id=card_id, user=user)

    # Obtener la instancia de SalesOrder basada en sale_order_id
    sale_order = get_object_or_404(SalesOrder, id=sale_order_id)

    # Crear la nueva tarea diaria
    daily_task = Task.objects.create(
        verb=verb,
        object=object_,
        sale_order=sale_order,  # Asignar la instancia de SalesOrder
        measurement=measurement,
        task_time=task_time,
        user=user
    )

    # Obtener el orden máximo actual para las tareas en esta tarjeta
    max_order = get_max_order(card)
    CardTaskOrder.objects.create(task=daily_task, card=card, order=max_order)

    # Volver a cargar las tareas ordenadas para la tarjeta
    tasks_ordered = CardTaskOrder.objects.filter(card=card).order_by('order').select_related('task')
    daily_tasks = tasks_ordered

    # Renderizar la lista actualizada de tareas
    return render(request, 'partials/daily-task-list.html', {'daily_tasks': daily_tasks, 'card_id': card.id})


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
    search_text = request.POST.get('search')
    card_id = request.POST.get('card_id')

    if not card_id:
        card_id = request.session.get('current_card_id')  # Intenta obtener de la sesión
        if not card_id:
            # Si todavía no se encuentra, puedes manejarlo con un error o una redirección
            return JsonResponse({'error': 'Card ID is required'}, status=400)

    print(f"search_task: card_id={card_id}")  # Depuración

    results = Task.objects.filter(user=request.user, verb__icontains=search_text)
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
    task_order = get_object_or_404(CardTaskOrder, pk=pk, card__user=request.user)
    task_order.state = not task_order.state
    task_order.save()

    # Actualizar la valoración de la Card
    card = task_order.card
    card.update_valuation()

    return HttpResponse(status=204)


# Iniciamos vista y metodos HTMX para tareas
def tasks(request):
    user_tasks = Task.objects.filter(user=request.user)
    context = {'form': TaskForm(), 'tasks': user_tasks}
    return render(request, 'tasks/task.html', context)

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
