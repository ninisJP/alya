from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, redirect

from datetime import date, timedelta

from .models import Technician, TechnicianCard, TechnicianCardTask, TechnicianTask
from .forms import TechnicianCardForm, TechnicianForm, TechnicianTaskForm

class TechniciansMonth(TemplateView):
    template_name = 'technicians_month.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener los parámetros del URL
        mes = self.kwargs.get('mes')
        anio = self.kwargs.get('anio')

        # Obtener los datos del informe para el mes y año especificados
        datos_informe = self.informe_tarjetas_del_mes(mes, anio)

        context['mes'] = mes  # Asegúrate de que mes sea un número
        context['anio'] = anio
        context['informe'] = datos_informe['informe_por_tecnico']

        return context

    def informe_tarjetas_del_mes(self, mes, anio):
        primer_dia_mes = date(anio, mes, 1)
        ultimo_dia_mes = primer_dia_mes + timedelta(days=28) + timedelta(days=4)
        ultimo_dia_mes = ultimo_dia_mes - timedelta(days=ultimo_dia_mes.day)

        # Obtener todas las tarjetas para el mes y año especificados
        tarjetas_del_mes = TechnicianCard.objects.filter(
            date__range=(primer_dia_mes, ultimo_dia_mes)
        ).order_by('technician', 'date')

        # Obtener todos los técnicos
        todos_los_tecnicos = Technician.objects.all()

        informe = {}
        for tecnico in todos_los_tecnicos:
            tecnico_id = tecnico.id
            informe[tecnico_id] = {
                'technician': f"{tecnico.name} {tecnico.lastname}",
                'dias_con_tarjeta': set(),
                'dias_sin_tarjeta': set(range(1, (ultimo_dia_mes - primer_dia_mes).days + 2))
            }

        # Rellenar los días con tarjeta
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



def create_technician(request):
    if request.method == 'POST':
        form = TechnicianForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_technician')
    else:
        form = TechnicianForm()

    return render(request, 'technician_form.html', {'form': form})

def create_technician_task(request):
    if request.method == 'POST':
        form = TechnicianTaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_technician_task')
    else:
        form = TechnicianTaskForm()

    return render(request, 'create_technician_task.html', {'form': form})

def create_technician_card(request, tecnico_id=None, dia=None, mes=None, anio=None):
    if request.method == 'POST':
        form = TechnicianCardForm(request.POST)
        if form.is_valid():
            technician_card = form.save(commit=False)
            technician_card.save()

            # Obtener el orden de las tareas
            orden_tareas = request.POST.get('orden_tareas', '')
            tarea_ids = orden_tareas.split(',')

            # Crear las relaciones TechnicianCardTask con el orden correcto
            for order, task_id in enumerate(tarea_ids, start=1):
                task = TechnicianTask.objects.get(id=task_id)
                TechnicianCardTask.objects.create(
                    technician_card=technician_card,
                    task=task,
                    order=order
                )

            return redirect('create_technician_card')
    else:
        if tecnico_id and dia and mes and anio:
            tecnico = get_object_or_404(Technician, id=tecnico_id)
            fecha = date(anio, mes, dia)
            form = TechnicianCardForm(initial={'technician': tecnico, 'date': fecha})
        else:
            form = TechnicianCardForm()

    return render(request, 'create_technician_card.html', {'form': form})


def view_technician_card(request, tecnico_id, dia, mes, anio):
    # Obtener el técnico
    tecnico = get_object_or_404(Technician, id=tecnico_id)

    # Crear la fecha específica para buscar la tarjeta
    fecha = date(anio, mes, dia)

    # Obtener la tarjeta del técnico para esa fecha específica
    tarjeta = get_object_or_404(TechnicianCard, technician=tecnico, date=fecha)

    context = {
        'tarjeta': tarjeta,
        'tecnico': tecnico,
        'fecha': fecha
    }
    return render(request, 'view_technician_card.html', context)
