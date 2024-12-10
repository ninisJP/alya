from django.db import models
from decimal import Decimal
from collections import defaultdict
import pandas as pd
import re
import openpyxl
from openpyxl import Workbook
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Sum, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from follow_control_card.forms import TaskForm
from accounting_order_sales.models import SalesOrder, SalesOrderItem
from .forms import (
    BudgetEditNewForm, 
    BudgetForm, 
    BudgetItemFormSet, 
    CatalogItemForm, 
    SearchCatalogItemForm, 
    NewBudgetItemForm, 
    EditBudgetItemForm, 
    BudgetUploadForm, 
    ExcelUploadForm, 
    AddBudgetItemForm
)
from django.core.cache import cache
from .models import Budget, BudgetItem, CatalogItem
from .utils import (
    export_budget_report_to_excel, 
    process_budget_excel, 
    process_sap_excel
)

def index_budget(request):
    budgets = Budget.objects.all()  # Recupera todos los presupuestos
    return render(request, 'index_budget.html', {'budgets': budgets})
  
def edit_budget_item_htmx(request, item_id):
    item = get_object_or_404(BudgetItem, id=item_id)
    
    print("Método HTTP:", request.method)  # Para depurar el método HTTP
    if request.method == 'POST':
        form = EditBudgetItemForm(request.POST, instance=item)
        
        if form.is_valid():
            # Actualizar valores de total_price en función de los datos actuales
            quantity = form.cleaned_data.get('quantity')
            custom_price = form.cleaned_data.get('custom_price') or item.item.price  # Usar precio del catálogo si está vacío
            custom_price_per_day = form.cleaned_data.get('custom_price_per_day') or item.item.price_per_day
            
            # Realizar el cálculo de total_price según la categoría del ítem
            if item.item.category in [CatalogItem.Category.HERRAMIENTA, CatalogItem.Category.MANODEOBRA, CatalogItem.Category.EPPS]:
                item.total_price = Decimal(custom_price_per_day) * Decimal(quantity) * Decimal(item.budget.budget_days)
            else:
                item.total_price = Decimal(custom_price) * Decimal(quantity)
            
            # Guardar el formulario con el total_price actualizado
            form.save()
            
            # Renderizar el template actualizado con el item editado
            return render(request, 'budget/item_row.html', {'item': item})
        else:
            print(form.errors)  # Imprimir errores del formulario si los hay
    else:
        form = EditBudgetItemForm(instance=item)

    # Devolver el formulario para edición
    return render(request, 'budget/edit_item_form.html', {'form': form, 'item': item})

def upload_budget_excel(request, budget_id):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']

        # Guardar temporalmente el archivo subido
        fs = FileSystemStorage()
        filename = fs.save(excel_file.name, excel_file)
        uploaded_file_url = fs.url(filename)

        # Procesar el archivo de Excel
        process_budget_excel(excel_file, budget_id)

        return redirect('detail_budget', pk=budget_id)

    return render(request, 'budget/upload_excel.html', {
        'budget_id': budget_id
    })

def upload_sap_excel(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id)

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        print("Archivo recibido:", excel_file)  # Verificar si el archivo se recibe

        try:
            # Llamar a la función que procesará el archivo
            print("Iniciando procesamiento del archivo SAP")
            process_sap_excel(excel_file, budget)  # Pasa la instancia `budget` en lugar de su `id`
            print("Procesamiento completado")

            return redirect('detail_budget', pk=budget_id)

        except Exception as e:
            print(f"Error al procesar el archivo: {str(e)}")
            return redirect('detail_budget', pk=budget_id)

    print("No se recibió un archivo Excel o no es un POST")
    return redirect('detail_budget', pk=budget_id)

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

    # Verificar si ya existe una orden de venta con el mismo sapcode que el budget_number
    existing_sales_order = SalesOrder.objects.filter(sapcode=budget.budget_number).first()

    # Iniciar una transacción atómica para garantizar la consistencia de los datos
    with transaction.atomic():
        if existing_sales_order:
            # Actualizar el campo days de la orden de venta existente
            existing_sales_order.days = budget.budget_days  # Asignar días del presupuesto
            existing_sales_order.save()

            # Lista para almacenar los códigos SAP presentes en el presupuesto
            sap_codes_in_budget = set()

            # Si ya existe una orden de venta, actualizamos o agregamos ítems
            for budget_item in budget.items.all():
                # Normalizar el código SAP del presupuesto
                sap_code = str(budget_item.item.sap).strip().upper()
                sap_codes_in_budget.add(sap_code)

                price_with_igv = (budget_item.custom_price or budget_item.item.price) * Decimal('1.18')
                total_price_with_igv = budget_item.total_price * Decimal('1.18') if budget_item.total_price else Decimal('0.00')

                # Buscar el ítem en la orden de venta existente, normalizando el código SAP
                sales_order_item = existing_sales_order.items.filter(sap_code__iexact=sap_code).first()

                if sales_order_item:
                    # Actualizar el ítem existente
                    sales_order_item.amount = budget_item.quantity
                    sales_order_item.price = price_with_igv
                    sales_order_item.price_total = total_price_with_igv
                    sales_order_item.unit_of_measurement = budget_item.unit or budget_item.item.unit
                    sales_order_item.category = budget_item.item.category
                    sales_order_item.description = budget_item.item.description
                    sales_order_item.custom_quantity = budget_item.custom_quantity
                    sales_order_item.custom_price_per_hour = budget_item.custom_price_per_hour
                    sales_order_item.save()
                    sales_order_item.update_remaining_requirement()
                else:
                    # Crear un nuevo ítem en la orden de venta
                    new_item = SalesOrderItem.objects.create(
                        salesorder=existing_sales_order,
                        sap_code=sap_code,
                        description=budget_item.item.description,
                        amount=budget_item.quantity,
                        price=price_with_igv,
                        price_total=total_price_with_igv,
                        unit_of_measurement=budget_item.unit or budget_item.item.unit,
                        category=budget_item.item.category,
                        custom_quantity=budget_item.custom_quantity,
                        custom_price_per_hour=budget_item.custom_price_per_hour,
                    )
                    new_item.update_remaining_requirement()

            # Obtener los códigos SAP de los ítems actuales en la orden de venta y normalizarlos
            sap_codes_in_sales_order = set(
                str(item.sap_code).strip().upper()
                for item in existing_sales_order.items.all()
            )

            # Mensajes de depuración
            print(f"SAP codes in budget: {sap_codes_in_budget}")
            print(f"SAP codes in sales order before update: {sap_codes_in_sales_order}")

            # Identificar los códigos SAP que deben eliminarse
            sap_codes_to_delete = sap_codes_in_sales_order - sap_codes_in_budget
            print(f"SAP codes to delete: {sap_codes_to_delete}")

            if sap_codes_to_delete:
                # Eliminar los SalesOrderItems cuyo código SAP está en sap_codes_to_delete
                items_to_delete = existing_sales_order.items.filter(
                    sap_code__in=sap_codes_to_delete
                )
                count_deleted = items_to_delete.count()
                items_to_delete.delete()
                messages.info(request, f"Se eliminaron {count_deleted} ítems de la orden de venta que ya no están en el presupuesto.")
            else:
                messages.info(request, "No hay ítems para eliminar de la orden de venta.")

            messages.success(request, f"Los precios y los ítems de la orden de venta existente con sapcode {existing_sales_order.sapcode} fueron actualizados con IGV.")
        else:
            # Crear una nueva orden de venta si no existe
            sales_order = SalesOrder.objects.create(
                sapcode=budget.budget_number,
                project=None,
                detail=f"Orden basada en el presupuesto {budget.budget_name}",
                date=budget.budget_date,
                days=budget.budget_days,
            )

            for budget_item in budget.items.all():
                sap_code = str(budget_item.item.sap).strip().upper()
                price_with_igv = (budget_item.custom_price or budget_item.item.price) * Decimal('1.18')
                total_price_with_igv = budget_item.total_price * Decimal('1.18') if budget_item.total_price else Decimal('0.00')

                new_item = SalesOrderItem.objects.create(
                    salesorder=sales_order,
                    sap_code=sap_code,
                    description=budget_item.item.description,
                    amount=budget_item.quantity,
                    price=price_with_igv,
                    price_total=total_price_with_igv,
                    unit_of_measurement=budget_item.unit or budget_item.item.unit,
                    category=budget_item.item.category,
                    custom_quantity=budget_item.custom_quantity,
                    custom_price_per_hour=budget_item.custom_price_per_hour,
                )
                new_item.update_remaining_requirement()

            messages.success(request, f"La orden de venta {sales_order.sapcode} fue creada exitosamente con IGV incluido.")

    return redirect('index_budget')

def export_budget_report(request, pk):
    return export_budget_report_to_excel(request, pk)

def catalog(request):
    # Formularios de creación y búsqueda
    form = CatalogItemForm()
    search_form = SearchCatalogItemForm()

    # Intentar obtener los datos desde el caché
    catalogs = cache.get('catalog_items')
    
    # Si no están en caché, obtener los datos de la base de datos
    if not catalogs:
        catalogs = CatalogItem.objects.all()
        # Guardar los ítems en caché por 1 hora
        cache.set('catalog_items', catalogs, timeout=3600)

    # Paginación
    paginator = Paginator(catalogs, 25)  # 25 ítems por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Contexto con los formularios y los ítems paginados
    context = {
        'form': form,
        'search': search_form,
        'catalogs': page_obj,  # Usamos page_obj para la paginación
    }

    # Renderizar la plantilla con el contexto
    return render(request, 'catalog/home.html', context)

def catalog_item_search(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        term = request.GET.get('term', '')
        
        # Filtramos los resultados, primero por el término de búsqueda
        items = CatalogItem.objects.all()

        if term:
            # Filtrar por descripción o SAP, dependiendo del término de búsqueda
            items = items.filter(
                models.Q(description__icontains=term) | models.Q(sap__icontains=term)
            )
        
        # Ordenamos los resultados por descripción
        items = items.order_by('description')
        
        # Paginamos los resultados para evitar devolver demasiados ítems de una vez
        paginator = Paginator(items, 100)  # Mostramos 10 resultados por página
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
    query = request.GET.get('q','')
    
    if query:
        catalogs = CatalogItem.objects.filter(Q(sap__contains=query)).order_by('-id')
    else:
        catalogs = CatalogItem.objects.all().order_by('-id')
    
    context = {'catalogs':catalogs, 'form':CatalogItemForm()}
    return render(request, 'catalog/list.html',context)

def upload_excel(request):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            try:
                # Verificar la extensión del archivo
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)  # Leer archivo CSV
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)  # Leer archivo Excel
                else:
                    messages.error(request, "Solo se permiten archivos .csv y .xlsx.")
                    return redirect('budget_catalog_excel')

                if df.empty:
                    messages.error(request, "El archivo está vacío.")
                    return redirect('budget_catalog_excel')

                # Columnas requeridas
                required_columns = ['Número de artículo', 'Descripción del artículo', 'Grupo de artículos', 'Unidad de medida de inventario', 'Último precio de compra']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    messages.error(request, f"El archivo no contiene las columnas necesarias: {', '.join(missing_columns)}")
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

                messages.success(request, "El archivo se ha procesado y los datos se han guardado o actualizado exitosamente.")
                return redirect('budget_catalog_excel')

            except pd.errors.ParserError as e:
                messages.error(request, f"Error de formato en el archivo: {e}")
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

def export_catalog(request):
    # Crear un archivo Excel en memoria
    wb = Workbook()
    ws = wb.active
    ws.title = "Catalogo"

    # Crear las cabeceras de las columnas (esto será el formato de exportación)
    ws.append(['Número de artículo', 'Descripción del artículo', 'Grupo de artículos', 'Unidad de medida de inventario','Último precio de compra',])

                            #     sap = str(row['Número de artículo']).strip()
                            # description = str(row['Descripción del artículo']).strip()
                            # category = str(row['Grupo de artículos']).strip()
                            # unit = str(row['Unidad de medida de inventario']).strip() if pd.notnull(row['Unidad de medida de inventario']) else 'UND'

                            # price_str = str(row['Último precio de compra']).strip()
                            # price_cleaned = re.sub(r'[^\d.,]', '', price_str).replace(',', '')
                            # price = float(price_cleaned) if price_cleaned else 0.0

    # Obtener todos los elementos del catálogo
    catalog_items = CatalogItem.objects.all()

    # Añadir los datos al archivo Excel, renombrando las columnas en el proceso
    for item in catalog_items:
        ws.append([item.sap, item.description, item.category, item.unit, item.price])

    # Preparar la respuesta HTTP para descargar el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="catalogo.xlsx"'

    # Guardar el archivo Excel en la respuesta HTTP
    wb.save(response)

    return response
