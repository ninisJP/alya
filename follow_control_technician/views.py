from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render, redirect
from datetime import date, datetime, timedelta
from accounting_order_sales.models import SalesOrder
from employee.models import Technician
from .models import TechnicianCard, TechnicianTask, TechnicianTaskGroup
from .forms import TechnicianCardForm, TechnicianCardTaskForm, TechnicianCardTaskFormSet, TechnicianCardTask, TechnicianTaskForm, TechnicianTaskGroupForm
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.shortcuts import render, redirect
from .forms import ExcelUploadForm, TechnicianTaskForm
from .models import TechnicianTask
from .utils import get_next_order_for_card_task, process_technician_tasks_excel
from django.shortcuts import render, redirect
from .forms import ExcelUploadForm, TechnicianTaskForm, AddTasksToGroupForm, EditGroupItemForm
from .models import TechnicianTask, TechnicianTaskGroupItem
from .utils import process_technician_tasks_excel
from django.db.models import Q

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

            # Detectar si el usuario presionó "Crear y Crear Otra"
            if 'save_and_create_another' in request.POST:
                # Redirigir de vuelta a la misma vista de creación
                return redirect(reverse('create_technician_card', kwargs={'mes': mes, 'anio': anio}))

            # Si se presionó "Guardar", redirigir a la lista de técnicos del mes
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


from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from .models import TechnicianCard, TechnicianCardTask

def view_technician_card(request, card_id):
    tarjeta = get_object_or_404(TechnicianCard, id=card_id)
    form = TechnicianCardTaskForm()

    # Obtener todas las tareas asociadas a esta tarjeta
    tareas_con_foto = TechnicianCardTask.objects.filter(technician_card=tarjeta).select_related('task')

    # Calcular los minutos totales de las tareas asociadas a esta tarjeta
    total_minutes = tareas_con_foto.aggregate(total_time=Sum('task__time'))['total_time'] or 0

    # Obtener todos los grupos de tareas
    grupos_tareas = TechnicianTaskGroup.objects.all()

    # Si es una solicitud HTMX (para agregar o eliminar tareas), devolvemos tanto las tareas como los minutos actualizados
    if request.htmx:
        return render(request, 'partials/technician_tasks_list.html', {
            'tareas_con_foto': tareas_con_foto,
            'total_minutes': total_minutes,  # Aseguramos que el total de minutos se pase
        })

    # Si no es una solicitud HTMX, devolvemos la vista completa
    context = {
        'tarjeta': tarjeta,
        'tecnico': tarjeta.technician,
        'fecha': tarjeta.date,
        'form': form,
        'tareas_con_foto': tareas_con_foto,
        'grupos_tareas': grupos_tareas,  # Pasar los grupos al contexto
        'total_minutes': total_minutes,  # Incluir el total de minutos en el contexto
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
                return redirect("technician_task") 
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

def techniciantask_search(request):
    query = request.GET.get('q','')
    
    if query:
        technicians_tasks = TechnicianTask.objects.filter(
            Q(verb__icontains=query) | Q(object__icontains=query) | Q(measurement__icontains=query) | Q(time__icontains=query)     # fields = ('verb', 'object', 'measurement', 'time')

        ).order_by('-id')
    else:
        technicians_tasks = TechnicianTask.objects.all().order_by('-id')
    
    context = {'tasks':technicians_tasks, 'form':TechnicianTaskForm()}
    return render(request,'technician_task/technician-task-list.html', context)


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
    sales_orders = SalesOrder.objects.all()

    tasks_by_date = {}
    all_day_events = []

    if sales_order_id:
        tasks = TechnicianCardTask.objects.filter(saler_order_id=sales_order_id).select_related('technician_card', 'task')
        print("Tasks found:", tasks)

        # Agrupamos las tareas por fecha y técnico, y las ordenamos por el campo `order`
        tasks_grouped_by_technician = {}
        for task in tasks:
            task_date = task.technician_card.date
            technician = task.technician_card.technician
            
            # Agrupamos tareas por fecha y técnico
            if (task_date, technician) not in tasks_grouped_by_technician:
                tasks_grouped_by_technician[(task_date, technician)] = []
                
            tasks_grouped_by_technician[(task_date, technician)].append(task)
        
        # Para cada día y técnico, organizamos las tareas en secuencia de acuerdo al orden
        for (task_date, technician), technician_tasks in tasks_grouped_by_technician.items():
            # Configuramos la hora de inicio
            start_time = datetime.combine(task_date, technician_tasks[0].technician_card.start_hour) if hasattr(technician_tasks[0].technician_card, 'start_hour') else datetime.combine(task_date, datetime.min.time()) + timedelta(hours=8)
            
            # Generamos un color único para cada técnico
            technician_name = f"{technician.first_name} {technician.last_name}"
            color = f"#{hash(technician_name) & 0xFFFFFF:06x}"

            # Ordenamos las tareas por el campo `order` y las agregamos secuencialmente
            for task in sorted(technician_tasks, key=lambda t: t.order):
                task_duration_hours = float(task.total_time or 0) / 60  # Convertimos minutos a horas
                end_time = start_time + timedelta(hours=task_duration_hours)

                # Inicializamos el día en `tasks_by_date` si no existe
                if task_date not in tasks_by_date:
                    tasks_by_date[task_date] = []

                # Agregamos cada tarea como evento separado en `tasks_by_date`
                tasks_by_date[task_date].append({
                    'title': f"{task.task.verb} {task.task.object}",
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'description': f"Tarea: {task.task.verb} {task.task.object} - Duración: {task.total_time} minutos",
                    'technician': technician_name,
                    'quantity': task.quantity,
                    'measurement': task.task.measurement,
                    'status': "Completado" if task.status else "Pendiente",
                    'color': color  # Color para identificar al técnico
                })

                # Actualizamos la hora de inicio para la siguiente tarea de este técnico
                start_time = end_time

        # Crear un evento de "All Day" para mostrar el total de tareas por día
        for task_date, daily_tasks in tasks_by_date.items():
            all_day_events.append({
                'title': f"{len(daily_tasks)} Tarea(s)",
                'start': task_date.isoformat(),
                'allDay': True,
                'tasks': [
                    {
                        'title': task['title'],
                        'technician': task['technician'],
                        'quantity': task['quantity'],
                        'total_time': task['description'].split('-')[1].strip(),
                        'measurement': task['measurement'],
                        'status': task['status']
                    }
                    for task in daily_tasks
                ]
            })

    return render(request, 'technician_calendar/technician_calendar.html', {
        'sales_orders': sales_orders,
        'selected_sales_order': sales_order_id,
        'tasks_by_date': tasks_by_date,
        'all_day_events': all_day_events  # Eventos "All Day" para el resumen
    })

def list_task_groups(request):
    task_groups = TechnicianTaskGroup.objects.all()
    form = TechnicianTaskGroupForm()
    return render(request, 'technician_groups/technician_task_group_list.html', {'task_groups': task_groups, 'form': form})

def create_task_group(request):
    if request.method == "POST":
        form = TechnicianTaskGroupForm(request.POST)
        if form.is_valid():
            new_group = form.save()
            return render(request, 'technician_groups/task_group_row.html', {'task_group': new_group})  # Renderizamos solo la fila nueva
    return HttpResponse(status=400)  # Devuelve un error si algo falla

from django.db.models import Sum

def detail_task_group(request, group_id):
    group = get_object_or_404(TechnicianTaskGroup, id=group_id)

    # Buscar tareas
    search_query = request.GET.get('search', '')  # Obtiene el término de búsqueda desde el GET
    if search_query:
        tasks = TechnicianTask.objects.filter(
            verb__icontains=search_query  # Filtra las tareas que contienen el término de búsqueda en 'verb'
        ).order_by('-time')  # Ordena por tiempo
    else:
        tasks = TechnicianTask.objects.all().order_by('-time')  # Muestra todas las tareas si no hay búsqueda

    # Inicializar total_minutes con 0
    total_minutes = 0

    # Calcular la suma de los minutos de las tareas que ya están en el grupo
    total_minutes = group.group_items.aggregate(total_time=Sum('task__time'))['total_time'] or 0

    # Calcular la suma de los minutos de las tareas seleccionadas solo cuando se envía un formulario
    if request.method == 'POST':
        # Agregar tareas al grupo
        if 'add_tasks' in request.POST:
            add_form = AddTasksToGroupForm(request.POST)
            if add_form.is_valid():
                selected_tasks = add_form.cleaned_data['tasks']  # Obtén las tareas seleccionadas
                # Sumar los tiempos de las tareas seleccionadas antes de agregarlas al grupo
                selected_time = selected_tasks.aggregate(total_time=Sum('time'))['total_time'] or 0
                total_minutes += selected_time  # Agregar los minutos de las tareas seleccionadas a total_minutes

                # Agregar las tareas al grupo
                for task in selected_tasks:
                    TechnicianTaskGroupItem.objects.create(
                        task_group=group,
                        task=task,
                        quantity=1,  # Default quantity
                        order=TechnicianTaskGroupItem.objects.filter(task_group=group).count() + 1,
                        saler_order=None  # Optional
                    )

                return redirect('detail_task_group', group_id=group.id)

        # Editar elementos del grupo
        elif 'edit_items' in request.POST:
            for item in group.group_items.all():
                form = EditGroupItemForm(request.POST, instance=item, prefix=f'item_{item.id}')
                if form.is_valid():
                    form.save()
            return redirect('detail_task_group', group_id=group.id)

        # Eliminar un elemento del grupo
        elif 'delete_item' in request.POST:
            item_id = request.POST.get('delete_item')
            item = TechnicianTaskGroupItem.objects.get(id=item_id)
            item.delete()
            return redirect('detail_task_group', group_id=group.id)

    add_form = AddTasksToGroupForm()
    items = group.group_items.all()
    edit_forms = [(item, EditGroupItemForm(instance=item, prefix=f'item_{item.id}')) for item in items]

    return render(request, 'technician_groups/task_group_detail.html', {
        'group': group,
        'add_form': add_form,
        'items_with_forms': edit_forms,
        'tasks': tasks,  # Pasa las tareas filtradas para mostrarlas en el formulario
        'search_query': search_query,
        'total_minutes': total_minutes,  # Pasa la suma total de minutos a la plantilla
    })


def delete_task_group(request, group_id):
    group = get_object_or_404(TechnicianTaskGroup, id=group_id)
    if request.method == "POST":
        group.delete()
        return redirect('list_task_groups')  # Redirigir a la lista de grupos
    return redirect('list_task_groups')

def associate_group_to_card(request, card_id):
    tarjeta = get_object_or_404(TechnicianCard, id=card_id)

    if request.method == "POST":
        group_id = request.POST.get("task_group")
        task_group = get_object_or_404(TechnicianTaskGroup, id=group_id)

        # Asociar el grupo a la tarjeta
        for group_item in task_group.group_items.all():
            TechnicianCardTask.objects.create(
                technician_card=tarjeta,
                task=group_item.task,
                quantity=group_item.quantity,
                total_time=group_item.task.time * group_item.quantity,
                saler_order=group_item.saler_order,
                order=group_item.order,
                task_group=group_item.task_group,
            )

        return redirect("view_technician_card", card_id=card_id)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import pandas as pd
from .models import TechnicianTaskGroup

def upload_task_group_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        try:
            # Aseguramos que el archivo esté disponible y en formato correcto
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                # Utilizamos pandas para leer el archivo excel
                df = pd.read_excel(file)

                # Procesar los datos del archivo Excel y crear los grupos
                for name in df.iloc[:, 0].dropna():  # Suponiendo que los nombres están en la primera columna
                    TechnicianTaskGroup.objects.get_or_create(name=name)

                messages.success(request, 'Archivo cargado correctamente.')
            else:
                messages.error(request, 'Por favor, sube un archivo Excel válido (.xlsx o .xls).')
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {str(e)}')

        return redirect('list_task_groups')  # Redirigir a la vista de la lista de grupos de tareas

    # Si no se envía un archivo, redirigir de nuevo
    messages.error(request, 'No se seleccionó ningún archivo.')
    return redirect('list_task_groups')

# Excel task - group
import pandas as pd
from .models import TechnicianTaskGroup, TechnicianTaskGroupItem, TechnicianTask
from django.contrib.auth.models import User

import pandas as pd
from .models import TechnicianTaskGroup, TechnicianTaskGroupItem, TechnicianTask

from django.shortcuts import render
from django.http import HttpResponse
from .models import TechnicianTaskGroup
import pandas as pd

import pandas as pd

import pandas as pd

def process_task_group_excel(file, sale_order=None):
    try:
        print("Iniciando lectura del archivo Excel...")
        df = pd.read_excel(file, header=0)

        # Limpiar los encabezados de la columna para eliminar espacios extras
        df.columns = df.columns.str.strip()

        # Mostrar los encabezados leídos para diagnóstico
        print("Encabezados del archivo:", df.columns)

        # Verificamos que el archivo tenga al menos las columnas necesarias
        if df.shape[1] < 6:
            print("Archivo no tiene las columnas necesarias.")
            raise ValueError("El archivo debe tener al menos 6 columnas: Grupo, Verbo, Objeto, Medida, Tiempo, Rutina, Frecuencia")

        print("Archivo leído correctamente. Procesando filas...")

        task_groups = {}  # Diccionario para almacenar los grupos de tareas por nombre
        errors = []  # Lista para almacenar errores por fila
        current_group = None  # Variable para almacenar el grupo actual

        for index, row in df.iterrows():
            try:
                # Asignar el grupo actual si es necesario
                if pd.notna(row['Subprocesos']):
                    current_group = row['Subprocesos']  # Actualizar el grupo solo si no es nulo

                # Usamos el grupo actual para todas las filas
                group_name = current_group
                verb = row['Verbo']
                object_ = row['Objeto']
                measurement = row['Medida']
                time = row['Tiempo']
                rutine = row['Rutina']
                frecuency = row['Frecuencia']

                # Verificar que los datos necesarios estén presentes
                if pd.isna(group_name) or pd.isna(verb) or pd.isna(object_) or pd.isna(measurement) or pd.isna(time) or pd.isna(rutine) or pd.isna(frecuency):
                    raise ValueError(f"Datos incompletos en la fila {index + 1}")

                # Buscar o crear el grupo de tareas
                if group_name not in task_groups:
                    task_group, created = TechnicianTaskGroup.objects.get_or_create(name=group_name)
                    task_groups[group_name] = task_group  # Guardar el grupo para uso posterior

                # Verificar si la tarea ya existe para evitar duplicados
                task, created = TechnicianTask.objects.get_or_create(
                    verb=verb,
                    object=object_,
                    measurement=measurement,
                    time=time,
                    rutine=rutine,
                    frecuency=frecuency
                )

                if created:
                    print(f"Tarea creada: {task}")
                else:
                    print(f"Tarea ya existe: {task}")

                # Crear el elemento del grupo de tareas (asociar la tarea con el grupo)
                task_group_item = TechnicianTaskGroupItem(
                    task_group=task_groups[group_name],  # Usamos task_group, que es el nombre correcto
                    task=task,
                    quantity=1,  # O tomar otro valor de las columnas del archivo, si es necesario
                    order=index  # Usamos el índice como orden en el grupo
                )
                task_group_item.save()  # Guardar el elemento del grupo en la base de datos

            except Exception as row_error:
                errors.append(f"Fila {index + 1}: {str(row_error)}")

        # Si no hubo errores, devolver éxito
        if errors:
            for error in errors:
                print("Error:", error)
            return False, "Errores en algunas filas. Revísalos en los detalles de la salida."

        print("Todas las tareas y grupos fueron procesados correctamente.")
        return True, None
    except Exception as e:
        print("Error durante el procesamiento del archivo:", str(e))
        return False, str(e)



def upload_task_group_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        # Obtener el archivo del formulario de carga
        file = request.FILES['file']

        # Llamar a la función para procesar el archivo Excel
        success, message = process_task_group_excel(file)

        if success:
            return redirect('list_task_groups')
        else:
            return HttpResponse(f"Error: {message}")
    return redirect('list_task_groups')
