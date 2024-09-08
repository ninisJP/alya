from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from datetime import date, timedelta
from employee.models import Technician
from .models import TechnicianCard
from .forms import TechnicianCardForm, TechnicianCardTaskFormSet, TechnicianCardTask

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
                'technician': f"{tecnico.first_name} {tecnico.last_name}",
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

def create_technician_card(request):
    if request.method == 'POST':
        card_form = TechnicianCardForm(request.POST)
        task_formset = TechnicianCardTaskFormSet(request.POST)

        if card_form.is_valid() and task_formset.is_valid():
            technician_card = card_form.save()

            # Guardar las tareas asociadas con la tarjeta del técnico
            task_formset.instance = technician_card
            task_formset.save()

            return redirect('success_url')  # Redirige a una URL de éxito

    else:
        card_form = TechnicianCardForm()
        task_formset = TechnicianCardTaskFormSet(queryset=TechnicianCardTask.objects.none())

    return render(request, 'create_technician_card.html', {
        'card_form': card_form,
        'task_formset': task_formset,
    })

def add_task_form(request):
    task_formset = TechnicianCardTaskFormSet(request.GET or None)
    return render(request, 'partials/task_form.html', {
        'task_formset': task_formset,
    })





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

