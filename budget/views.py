from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from django.http import HttpResponse, JsonResponse
from follow_control_card.forms import TaskForm
from .forms import BudgetForm, BudgetItemFormSet, CatalogItemForm, SearchCatalogItemForm, NewBudgetItemForm, EditBudgetItemForm
from .models import Budget, BudgetItem, CatalogItem
from .utils import export_budget_report_to_excel
from accounting_order_sales.models import SalesOrder, SalesOrderItem
from django.http import HttpResponse
from django.contrib import messages
from alya import utils
from django.core.paginator import Paginator


def index_budget(request):
    budgets = Budget.objects.all()  # Recupera todos los presupuestos
    return render(request, 'index_budget.html', {'budgets': budgets})

def catalog_item_search(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        term = request.GET.get('term', '')
        items = CatalogItem.objects.filter(description__icontains=term).order_by('description')
        
        # Paginamos los resultados para evitar devolver demasiados ítems de una vez
        paginator = Paginator(items, 10)  # Mostramos 10 resultados por página
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        results = []
        for item in page_obj:
            results.append({
                'id': item.id,
                'text': f'{item.sap} - {item.description}',
            })
        
        return JsonResponse({
            'results': results,
            'pagination': {
                'more': page_obj.has_next()  # Indica si hay más resultados
            }
        })
    else:
        return JsonResponse({'results': []})
    
def create_budget(request):
    if request.method == 'POST':
        print("Recibida solicitud POST en create_budget")
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            formset = BudgetItemFormSet(request.POST, instance=budget)
            print(f"Formset válido: {formset.is_valid()}")
            if formset.is_valid():
                budget.save()
                formset.save()
                print("Presupuesto y detalles guardados exitosamente")
                return redirect('detail_budget', pk=budget.pk)
            else:
                print(f"Errores en el formset: {formset.errors}")
        else:
            print(f"Errores en el formulario: {form.errors}")
        return render(request, 'budget/budget_form.html', {
            'form': form,
            'formset': formset,
        })
    else:
        print("Recibida solicitud GET en create_budget")
        form = BudgetForm()
        formset = BudgetItemFormSet()
    return render(request, 'budget/budget_form.html', {
        'form': form,
        'formset': formset,
    })

from .forms import AddBudgetItemForm
from collections import defaultdict

def detail_budget(request, pk):
    # Obtener el presupuesto por su primary key (pk)
    budget = get_object_or_404(Budget, pk=pk)
    items_by_category = defaultdict(list)

    # Agrupar los ítems del presupuesto por categoría
    for item in budget.items.all():
        items_by_category[item.item.category].append(item)

    # Inicializar el formulario vacío
    form = AddBudgetItemForm()

    # Renderizar la plantilla principal
    return render(request, 'budget/detail_budget.html', {
        'budget': budget,
        'items_by_category': dict(items_by_category),
        'form': form  # Pasar el formulario a la plantilla
    })

    
def add_budget_item_htmx(request, pk):
    budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        form = AddBudgetItemForm(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.budget = budget
            new_item.save()

            # Agrupar los ítems del presupuesto por categoría
            items_by_category = defaultdict(list)
            for item in budget.items.all():
                items_by_category[item.item.category].append(item)

            # Renderizar solo el fragmento con los ítems actualizados
            return render(request, 'budget/item_list.html', {
                'items_by_category': dict(items_by_category),
                'budget': budget  # Asegúrate de pasar también el presupuesto si es necesario
            })
    else:
        return redirect('detail_budget', pk=pk)
    
def delete_budget_item_htmx(request, item_id):
    item = get_object_or_404(BudgetItem, id=item_id)
    budget = item.budget  # Obtenemos el presupuesto al que pertenece el ítem

    # Eliminar el ítem
    item.delete()

    # Volver a agrupar los ítems restantes por categoría
    items_by_category = defaultdict(list)
    for remaining_item in budget.items.all():
        items_by_category[remaining_item.item.category].append(remaining_item)

    # Renderizar solo el fragmento actualizado con los ítems
    return render(request, 'budget/item_list.html', {
        'items_by_category': dict(items_by_category),
        'budget': budget,
    })
    
def edit_budget_item_htmx(request, item_id):
    item = get_object_or_404(BudgetItem, id=item_id)
    
    print("Método HTTP:", request.method)  # Para depurar el método HTTP
    if request.method == 'POST':
        form = EditBudgetItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            # Después de guardar, renderizamos nuevamente el ítem actualizado
            return render(request, 'budget/item_row.html', {'item': item})
    else:
        form = EditBudgetItemForm(instance=item)

    # Devolver el formulario para edición
    return render(request, 'budget/edit_item_form.html', {'form': form, 'item': item})



def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'El presupuesto ha sido eliminado exitosamente.')
        return redirect('index_budget')  # Redirigir a la lista de presupuestos

    return render(request, 'budget/delete_budget.html', {'budget': budget})


def duplicate_budget(request, pk):
    # Obtener el presupuesto original utilizando el 'pk'
    original_budget = get_object_or_404(Budget, pk=pk)

    # Duplicar el presupuesto
    duplicated_budget = Budget.objects.get(pk=original_budget.pk)
    duplicated_budget.pk = None  # Esto asegura que se cree un nuevo presupuesto
    duplicated_budget.budget_name = f"{original_budget.budget_name} (Duplicado)"
    duplicated_budget.save()

    # Duplicar los ítems asociados
    for item in original_budget.items.all():
        duplicated_item = BudgetItem.objects.get(pk=item.pk)
        duplicated_item.pk = None  # Asegura que se cree un nuevo BudgetItem
        duplicated_item.budget = duplicated_budget  # Asigna el nuevo presupuesto
        duplicated_item.save()

    # Redirigir a la vista de detalle del nuevo presupuesto
    return redirect('detail_budget', pk=duplicated_budget.pk)

def create_sales_order_from_budget(request, budget_id):
    # Obtener el presupuesto seleccionado
    budget = get_object_or_404(Budget, id=budget_id)
    
    # Crear la orden de venta con los datos básicos, dejando 'project' como null inicialmente y sapcode="000"
    sales_order = SalesOrder.objects.create(
        sapcode=0,  # Valor por defecto (SAP 000)
        project=None,  # Proyecto nulo, será agregado más tarde
        detail=f"Orden basada en el presupuesto {budget.budget_name}",
        date=budget.budget_date,
    )
    
    # Iterar sobre los items del presupuesto y crear items de la orden de venta
    for budget_item in budget.items.all():
        SalesOrderItem.objects.create(
            salesorder=sales_order,
            sap_code=budget_item.item.sap,
            description=budget_item.item.description,
            amount=budget_item.quantity,
            price=budget_item.item.price,  # Precio unitario
            price_total=budget_item.total_price,  # Precio total
            unit_of_measurement=budget_item.item.unit,
        )
    
    # Agregar un mensaje de éxito
    messages.success(request, f"La orden de venta {sales_order.sapcode} fue creada exitosamente.")
    
    # Redirigir a la vista principal de presupuestos
    return redirect('index_budget')

def export_budget_report(request, pk):
    return export_budget_report_to_excel(request, pk)

def catalog(request):
    user_tasks = CatalogItem.objects.all()
    context = {'form': TaskForm(), 'tasks': user_tasks}
    return render(request, '', context)

# CATALOG
def catalog(request):
    # Formularios de creación y búsqueda
    form = CatalogItemForm()
    search_form = SearchCatalogItemForm()

    # Listado de ítems de catálogo
    catalogs = CatalogItem.objects.all()

    context = {
        'form': form,
        'search': search_form,
        'catalogs': catalogs,
    }

    return render(request, 'catalog/home.html', context)

def catalog_edit(request, catalog_id):
    catalog = get_object_or_404(CatalogItem, id=catalog_id)

    if request.method == 'POST':
        form = CatalogItemForm(request.POST, instance=catalog)
        if form.is_valid():
            form.save()
            # Después de guardar, renderizar el lista ítem
            catalog = get_object_or_404(CatalogItem, id=catalog_id)
            return render(request, 'catalog/list_element.html', {'catalog': catalog})
    else:
        form = CatalogItemForm(instance=catalog)

    context = {'form': form, 'catalog': catalog}
    return render(request, 'catalog/edit.html', context)

def catalog_new(request):
    context = {}
    if request.method == 'POST':
        form = CatalogItemForm(request.POST)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
        context['status'] = status

    context['form'] = CatalogItemForm()

    return render(request, 'catalog/form.html', context)

def catalog_search(request):
    context = {}
    if request.method == 'POST':
        form = SearchCatalogItemForm(request.POST)
        if form.is_valid():

            # Search catalogs
            if form.cleaned_data['sap'] and not form.cleaned_data['description'] :
                # Only SAP
                status, catalogs = utils.search_model(CatalogItem.objects.all(), 'sap', form.cleaned_data['sap'], accept_all=True)
            elif form.cleaned_data['sap'] and form.cleaned_data['description'] :
                # SAP and description
                status, catalogs = utils.search_model(CatalogItem.objects.all(), 'sap', form.cleaned_data['sap'], accept_all=True)
                status, catalogs = utils.search_model(catalogs, 'description', form.cleaned_data['description'], accept_all=True)
            elif form.cleaned_data['description']:
                # Only description
                status, catalogs = utils.search_model(CatalogItem.objects.all(), 'description', form.cleaned_data['description'], accept_all=True)
            else :
                # Item
                catalogs = CatalogItem.objects.all()
                status = 0

            # Sort
            catalogs = catalogs.order_by('sap')

            context['catalogs'] = catalogs
            context['search_status'] = status
    context['search'] = SearchCatalogItemForm()
    return render(request, 'catalog/list.html', context)

import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ExcelUploadForm
from .models import CatalogItem
import re  # Biblioteca para manejar expresiones regulares

from django.db import transaction

def upload_excel(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            
            try:
                df = pd.read_csv(file)
                
                if df.empty:
                    messages.error(request, "El archivo está vacío.")
                    return redirect('budget_catalog_excel')

                required_columns = ['Número de artículo', 'Descripción del artículo', 'Grupo de artículos', 'Unidad de medida de inventario', 'Último precio de compra']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f"El archivo CSV no contiene las columnas necesarias: {', '.join(missing_columns)}")
                    return redirect('budget_catalog_excel')

                items_to_create = []

                # Usar una transacción para manejar todas las inserciones
                with transaction.atomic():
                    for _, row in df.iterrows():
                        try:
                            if pd.isnull(row['Número de artículo']) or pd.isnull(row['Descripción del artículo']):
                                continue
                            
                            sap = str(row['Número de artículo']).strip()
                            description = str(row['Descripción del artículo']).strip()
                            category = str(row['Grupo de artículos']).strip()
                            unit = str(row['Unidad de medida de inventario']).strip() if pd.notnull(row['Unidad de medida de inventario']) else 'UND'
                            
                            price_str = str(row['Último precio de compra']).strip()
                            price_cleaned = re.sub(r'[^\d.,]', '', price_str).replace(',', '')
                            price = float(price_cleaned) if price_cleaned else 0.0

                            item, created = CatalogItem.objects.update_or_create(
                                sap=sap,
                                defaults={
                                    'description': description,
                                    'category': category,
                                    'unit': unit,
                                    'price': price,
                                    'price_per_day': 0.0
                                }
                            )
                            items_to_create.append(item)

                        except Exception as e:
                            print(f"Error procesando la fila: {e}")
                            continue

                if items_to_create:
                    CatalogItem.objects.bulk_create(items_to_create, ignore_conflicts=True)
                
                messages.success(request, "El archivo CSV se ha procesado y los datos se han guardado o actualizado exitosamente.")
                return redirect('budget_catalog_excel')

            except pd.errors.ParserError as e:
                messages.error(request, f"Error de formato en el archivo CSV: {e}")
                return redirect('budget_catalog_excel')

            except ValueError as e:
                messages.error(request, f"Error de valor: {e}")
                return redirect('budget_catalog_excel')

            except KeyError as e:
                messages.error(request, f"Columna no encontrada: {e}")
                return redirect('budget_catalog_excel')

            except Exception as e:
                messages.error(request, f"Error inesperado: {e}")
                return redirect('budget_catalog_excel')

    else:
        form = ExcelUploadForm()
    
    return render(request, 'upload_excel.html', {'form': form})
