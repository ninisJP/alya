from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from datetime import date, timedelta
from employee.models import Technician
from .models import TechnicianCard, TechnicianTask
from .forms import TechnicianCardForm, TechnicianCardTaskFormSet, TechnicianCardTask, TechnicianTaskForm
from django.views.decorators.http import require_http_methods

class TechniciansMonth(TemplateView):
    template_name = 'technicians_month.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mes = self.kwargs.get('mes')
        anio = self.kwargs.get('anio')

        datos_informe = self.informe_tarjetas_del_mes(mes, anio)

        context['mes'] = mes 
        context['anio'] = anio
        context['informe'] = datos_informe['informe_por_tecnico']

        return context

    def informe_tarjetas_del_mes(self, mes, anio):
        primer_dia_mes = date(anio, mes, 1)
        ultimo_dia_mes = primer_dia_mes + timedelta(days=28) + timedelta(days=4)
        ultimo_dia_mes = ultimo_dia_mes - timedelta(days=ultimo_dia_mes.day)

        tarjetas_del_mes = TechnicianCard.objects.filter(
            date__range=(primer_dia_mes, ultimo_dia_mes)
        ).order_by('technician', 'date')

        todos_los_tecnicos = Technician.objects.all()

        informe = {}
        for tecnico in todos_los_tecnicos:
            tecnico_id = tecnico.id
            informe[tecnico_id] = {
                'technician': f"{tecnico.first_name} {tecnico.last_name}",
                'dias_con_tarjeta': set(),
                'dias_sin_tarjeta': set(range(1, (ultimo_dia_mes - primer_dia_mes).days + 2))
            }

        for tarjeta in tarjetas_del_mes:
            tecnico_id = tarjeta.technician.id
            informe[tecnico_id]['dias_con_tarjeta'].add(tarjeta.date.day)
            informe[tecnico_id]['dias_sin_tarjeta'].discard(tarjeta.date.day)

        for tecnico_id, datos in informe.items():
            datos['dias_con_tarjeta'] = sorted(list(datos['dias_con_tarjeta']))
            datos['dias_sin_tarjeta'] = sorted(list(datos['dias_sin_tarjeta']))

        return {
            'mes': primer_dia_mes.strftime('%B'),
            'anio': primer_dia_mes.year,
            'informe_por_tecnico': informe
        }

def create_technician_card(request, mes, anio):
    if request.method == 'POST':
        card_form = TechnicianCardForm(request.POST)
        task_formset = TechnicianCardTaskFormSet(request.POST)

        if card_form.is_valid() and task_formset.is_valid():
            technician_card = card_form.save()

            task_formset.instance = technician_card
            task_formset.save()

            return redirect(reverse('technicians_month', kwargs={'mes': mes, 'anio': anio}))
        else:
            print(card_form.errors)
            print(task_formset.errors)

    else:
        card_form = TechnicianCardForm()
        task_formset = TechnicianCardTaskFormSet(queryset=TechnicianCardTask.objects.none())

    return render(request, 'technician_card/create_technician_card.html', {
        'card_form': card_form,
        'task_formset': task_formset,
        'mes': mes,
        'anio': anio,
    })

def edit_technician_card(request, card_id, mes, anio):
    technician_card = get_object_or_404(TechnicianCard, id=card_id)
    
    if request.method == 'POST':
        card_form = TechnicianCardForm(request.POST, instance=technician_card)
        task_formset = TechnicianCardTaskFormSet(request.POST, instance=technician_card)

        if card_form.is_valid() and task_formset.is_valid():
            card_form.save()
            task_formset.save()
            return redirect(reverse('technicians_month', kwargs={'mes': mes, 'anio': anio}))
        else:
            print(card_form.errors)
            print(task_formset.errors)
    else:
        card_form = TechnicianCardForm(instance=technician_card)
        task_formset = TechnicianCardTaskFormSet(instance=technician_card)

    return render(request, 'technician_card/edit_technician_card.html', {
        'card_form': card_form,
        'task_formset': task_formset,
        'mes': mes,
        'anio': anio,
    })
    
def view_technician_card(request, tecnico_id, dia, mes, anio):
    tecnico = get_object_or_404(Technician, id=tecnico_id)
    fecha = date(anio, mes, dia)
    tarjeta = get_object_or_404(TechnicianCard, technician=tecnico, date=fecha)
    tareas_con_foto = tarjeta.tasks.filter(photo__isnull=False)


    context = {
        'tarjeta': tarjeta,
        'tecnico': tecnico,
        'fecha': fecha,
        'tareas_con_foto': tareas_con_foto,
    }
    return render(request, 'technician_card/view_technician_card.html', context)

def delete_technician_card(request, card_id):
    technician_card = get_object_or_404(TechnicianCard, id=card_id)
    if request.method == 'POST':
        technician_card.delete()
        return redirect(reverse('technicians_month', kwargs={'mes': technician_card.date.month, 'anio': technician_card.date.year}))

    return redirect(reverse('technicians_month', kwargs={'mes': technician_card.date.month, 'anio': technician_card.date.year}))

@require_http_methods(["PATCH"])
def technician_task_state(request, pk):
    task = get_object_or_404(TechnicianCardTask, pk=pk)
    if task.status == 'not_done':
        task.status = 'incomplete'
    elif task.status == 'incomplete':
        task.status = 'completed'
    else:
        task.status = 'not_done'

    task.save()

    return JsonResponse({"message": "Estado de la tarea actualizado correctamente."})



#Technicians tasks HTMX
def technician_task(request):
    technicians_tasks = TechnicianTask.objects.all()
    context = {'form': TechnicianTaskForm(), 'tasks': technicians_tasks}
    return render(request, 'technician_task/technician-task.html', context)

def create_technician_task(request):
    if request.method == 'POST':
        form = TechnicianTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False) 
            task.save()
            technician_tasks = TechnicianTask.objects.all()
            context = {'tasks': technician_tasks}
            return render(request, 'technician_task/technician-task-list.html', context)
    else:
        form = TechnicianTaskForm()

    return render(request, 'technician_task/technician-task-form.html', {'form': form})

def edit_technician_task(request, task_id):
    task = get_object_or_404(TechnicianTask, id=task_id)
    if request.method == 'GET':
        form = TechnicianTaskForm(instance=task)
        return render(request, 'technician_task/technician-task-edit.html', {'form': form, 'task': task})
    elif request.method == 'POST':
        form = TechnicianTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            technician_tasks = TechnicianTask.objects.all()
            return render(request, 'technician_task/technician-task-list.html', {'tasks': technician_tasks})
    return HttpResponse(status=405)


def delete_technician_task(request, task_id):
    task = get_object_or_404(TechnicianTask, id=task_id)  
    if request.method == 'DELETE':
        task.delete()
        return render(request, 'technician_task/technician-task-list.html')
    return HttpResponse(status=405)
