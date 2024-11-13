from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from datetime import date, timedelta
from accounting_order_sales.models import SalesOrder
from employee.models import Technician
from .models import TechnicianCard, TechnicianTask
from .forms import TechnicianCardForm, TechnicianCardTaskForm, TechnicianCardTaskFormSet, TechnicianCardTask, TechnicianTaskForm
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.shortcuts import render, redirect
from .forms import ExcelUploadForm, TechnicianTaskForm
from .models import TechnicianTask
from .utils import get_next_order_for_card_task, process_technician_tasks_excel
from django.shortcuts import render, redirect
from .forms import ExcelUploadForm, TechnicianTaskForm
from .models import TechnicianTask
from .utils import process_technician_tasks_excel

class TechniciansMonth(TemplateView):
    template_name = 'technicians_month.html'
    
    def dispatch(self, request, *args, **kwargs):
        hoy = now().date()
        if int(self.kwargs.get('mes')) != hoy.month or int(self.kwargs.get('anio')) != hoy.year:
            return redirect(reverse('technicians_month', kwargs={'mes': hoy.month, 'anio': hoy.year}))
        return super().dispatch(request, *args, **kwargs)

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
            informe[tecnico_id]['dias_con_tarjeta'].add(
                (tarjeta.date.day, tarjeta.id)  # Usamos una tupla en lugar de un diccionario
            )
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

def view_technician_card(request, card_id):
    tarjeta = get_object_or_404(TechnicianCard, id=card_id)
    form = TechnicianCardTaskForm()

    # Obtener las tareas asociadas a esta tarjeta
    tareas_con_foto = TechnicianCardTask.objects.filter(technician_card=tarjeta).select_related('task')

    context = {
        'tarjeta': tarjeta,
        'tecnico': tarjeta.technician,
        'fecha': tarjeta.date,
        'form': form,
        'tareas_con_foto': tareas_con_foto,
    }
    return render(request, 'technician_card/view_technician_card.html', context)

def add_technician_task(request, card_id):
    tarjeta = get_object_or_404(TechnicianCard, id=card_id)
    if request.method == 'POST':
        form = TechnicianCardTaskForm(request.POST)
        if form.is_valid():
            nueva_tarea = form.save(commit=False)
            nueva_tarea.technician_card = tarjeta
            nueva_tarea.order = get_next_order_for_card_task(tarjeta)  # Asignar el orden a la nueva tarea
            nueva_tarea.save()

            # Renderizamos la lista de tareas actualizada como partial para HTMX
            tareas_con_foto = TechnicianCardTask.objects.filter(technician_card=tarjeta).select_related('task')
            return render(request, 'partials/technician_tasks_list.html', {'tareas_con_foto': tareas_con_foto})

    # Si el formulario no es válido o no es POST, redirigir al detalle de la tarjeta
    return redirect('view_technician_card', card_id=card_id)

def delete_technician_card_task(request, task_id):
    task = get_object_or_404(TechnicianCardTask, id=task_id)
    card = task.technician_card  # Get the associated technician card
    task.delete()  # Delete the task from the card

    # Get the updated list of tasks
    tareas_con_foto = TechnicianCardTask.objects.filter(technician_card=card).select_related('task')

    # Render the updated tasks list partial for HTMX
    return render(request, 'partials/technician_tasks_list.html', {'tareas_con_foto': tareas_con_foto})



def delete_technician_card(request, card_id):
    technician_card = get_object_or_404(TechnicianCard, id=card_id)
    if request.method == 'POST':
        technician_card.delete()
        return redirect(reverse('technicians_month', kwargs={'mes': technician_card.date.month, 'anio': technician_card.date.year}))

    return redirect(reverse('technicians_month', kwargs={'mes': technician_card.date.month, 'anio': technician_card.date.year}))

@require_http_methods(["PATCH"])
def technician_task_state(request, pk):
    task = get_object_or_404(TechnicianCardTask, pk=pk)
    task.status = not task.status
    task.save()

    return JsonResponse({"message": "Estado de la tarea actualizado correctamente."})

def technician_task(request):
    technicians_tasks = TechnicianTask.objects.all()
    excel_form = ExcelUploadForm()
    form = TechnicianTaskForm()

    if request.method == "POST" and request.FILES.get("file"):
        excel_form = ExcelUploadForm(request.POST, request.FILES)
        if excel_form.is_valid():
            file = excel_form.cleaned_data["file"]
            print("Archivo recibido:", file.name)
            success, error = process_technician_tasks_excel(file)
            if success:
                print("Tareas guardadas exitosamente.")
                return redirect("technician_task")  # Redirige si se procesó exitosamente
            else:
                print("Error en el procesamiento del archivo:", error)
                excel_form.add_error(None, f"Error al procesar el archivo: {error}")
        else:
            print("Formulario de Excel no válido.")

    context = {
        'excel_form': excel_form,
        'form': form,
        'tasks': technicians_tasks
    }
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

def technician_calendar(request):
    sales_order_id = request.GET.get('sales_order')
    sales_orders = SalesOrder.objects.all()  # Menú de selección de órdenes de venta

    tasks_by_date = {}
    if sales_order_id:
        tasks = TechnicianCardTask.objects.filter(saler_order_id=sales_order_id)
        print("Tasks found:", tasks)  # Verifica las tareas encontradas
        for task in tasks:
            task_date = task.technician_card.date
            if task_date not in tasks_by_date:
                tasks_by_date[task_date] = []
            tasks_by_date[task_date].append(task)

    print("Tasks by date:", tasks_by_date)  # Verifica el diccionario organizado por fecha

    return render(request, 'technician_calendar/technician_calendar.html', {
        'sales_orders': sales_orders,
        'selected_sales_order': sales_order_id,
        'tasks_by_date': tasks_by_date,
    })