import traceback
import pdfplumber
import pandas as pd
import logging
import re
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Sum
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.timezone import localdate
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, FormView
from alya.utils import send_state_change_email
from logistic_requirements.forms import RequirementOrderForm, RequirementOrderItemFormSet
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from logistic_suppliers.models import Suppliers
from .forms import (
    PurchaseOrderForm,
    PurchaseOrderItemForm,
    SalesOrderForm,
    ItemSalesOrderExcelForm,
    ItemSalesOrderForm,
    BankForm,
    UploadBankStatementForm,
    CollectionOrdersForm
)
from .models import (
    Bank,
    BankStatements,
    CollectionOrders,
    PurchaseOrder,
    PurchaseOrderItem,
    Rendition,
    SalesOrder,
    SalesOrderItem,
)
from .utils import extraer_datos_pdf, procesar_archivo_excel
from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Prefetch
import json
from django.views.decorators.csrf import csrf_exempt

def salesorder(request):
    salesorders = SalesOrder.objects.all().order_by("-id")
    context = {'form': SalesOrderForm(), 'salesorders': salesorders} 
    return render(request, 'salesorder/sales_index.html', context)

def create_salesorder(request):
    if request.method == 'POST':
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            form.save()
            salesorders = SalesOrder.objects.all().order_by("-id")
            context = {'salesorders': salesorders}
            return render(request, 'salesorder/salesorder-list.html', context)
    else:
        form = SalesOrderForm()
    return render(request, 'salesorder/salesorder-form.html', {'form': form})

def edit_salesorder(request, salesorder_id):
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    if request.method == 'GET':
        form = SalesOrderForm(instance=salesorder)
        return render(request, 'salesorder/salesorder-edit.html', {'form': form, 'salesorder': salesorder})
    elif request.method == 'POST':
        form = SalesOrderForm(request.POST, instance=salesorder)
        if form.is_valid():
            form.save()
            salesorders = SalesOrder.objects.all().order_by("-id") 
            return render(request, 'salesorder/salesorder-list.html', {'salesorders': salesorders})
    return HttpResponse(status=405)

def delete_salesorder(request, salesorder_id):
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    if request.method == 'DELETE':
        salesorder.delete()
        salesorders = SalesOrder.objects.all().order_by("-id") 
        return render(request, 'salesorder/salesorder-list.html', {'salesorders': salesorders})
    return HttpResponse(status=405)

def items_salesorder(request, salesorder_id):
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    items = SalesOrderItem.objects.filter(salesorder=salesorder)

    if request.method == "POST":
        form = ItemSalesOrderForm(request.POST)
        excel_form = ItemSalesOrderExcelForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.salesorder = salesorder
            item.save()
            items = SalesOrderItem.objects.filter(salesorder=salesorder)
            return render(request, 'itemsalesorder/item-salesorder-list.html', {'items': items})

        if excel_form.is_valid():
            archivo_excel = request.FILES['archivo_excel']
            procesar_archivo_excel(archivo_excel, salesorder_id)
            items = SalesOrderItem.objects.filter(salesorder=salesorder)
            return render(request, 'itemsalesorder/item-salesorder-list.html', {'items': items})

    else:
        form = ItemSalesOrderForm()
        excel_form = ItemSalesOrderExcelForm()

    context = {
        'salesorder': salesorder,
        'items': items,
        'form': form,
        'excel_form': excel_form
    }

    return render(request, 'itemsalesorder/item-salesorder.html', context)

def quick_create_purchaseorder(request, salesorder_id):
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    items = SalesOrderItem.objects.filter(salesorder=salesorder)

    if request.method == "POST":
        # Obtenemos el ID del item desde el formulario y la cantidad
        item_id = request.POST.get("item_id")
        quantity_requested = int(request.POST.get("quantity_requested"))

        sales_order_item = get_object_or_404(SalesOrderItem, id=item_id)
        
        # Creamos la PurchaseOrder basada en los detalles del SalesOrder
        purchase_order = PurchaseOrder.objects.create(
            salesorder=salesorder,
            description=f"Orden de Compra rápida para {sales_order_item.description}",
            requested_date=request.POST.get('requested_date', None),  # Opcional
            scheduled_date=request.POST.get('scheduled_date', None),  # Opcional
            requested_by=request.user.username  # Asumimos que el usuario actual está creando la orden
        )

        # Creamos el PurchaseOrderItem basado en el SalesOrderItem
        purchase_order_item = PurchaseOrderItem.objects.create(
            purchaseorder=purchase_order,
            sales_order_item=sales_order_item,
            sap_code=sales_order_item.sap_code,
            quantity_requested=quantity_requested,  # Usamos la cantidad ingresada por el usuario
            price=sales_order_item.price,
            price_total=sales_order_item.price * quantity_requested,
            supplier=None  # Este campo puede ser opcional o predeterminado
        )

        return redirect('purchaseorder_list')  # Redirige a la lista de órdenes de compra

    return render(request, 'itemsalesorder/item-salesorder.html', {
        'salesorder': salesorder,
        'items': items,
    })

def general_purchaseorder(request):
    # Obtener los parámetros del rango de fechas (si existen)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Si no se han proporcionado fechas, mostrar las órdenes sin scheduled_date
    if not start_date and not end_date:
        purchase_orders = PurchaseOrder.objects.filter(scheduled_date__isnull=True)
    else:
        # Si se proporcionan fechas, buscar entre esas dos fechas
        if not end_date:
            end_date = localdate()  # Si solo se proporciona la fecha de inicio, se asume que el rango termina hoy

        purchase_orders = PurchaseOrder.objects.filter(
            scheduled_date__range=[start_date, end_date]
        )

    context = {
        'purchase_orders': purchase_orders,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'purchaseorder/general_purchaseorder.html', context)

# Ordenes de compra
def purchase_orders(request, salesorder_id):
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    purchase_orders = PurchaseOrder.objects.filter(salesorder=salesorder)

    context = {
        'salesorder': salesorder,
        'purchase_orders': purchase_orders,
    }

    return render(request, 'purchaseorder/purchaseorder_list.html', context)

def edit_purchase_order(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    ItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=0)

    if request.method == 'POST':
        order_form = PurchaseOrderForm(request.POST, instance=order)
        item_formset = ItemFormSet(request.POST, queryset=PurchaseOrderItem.objects.filter(purchaseorder=order))

        if order_form.is_valid() and item_formset.is_valid():
            order_form.save()
            
            # Guardar cada ítem y recalcular el price_total
            items = item_formset.save(commit=False)
            for item in items:
                item.price_total = item.price * item.quantity_requested  # Recalcular
                item.save()
            
            return render(request, 'purchaseorder/purchaseorder_partial.html', {'order': order})
    else:
        order_form = PurchaseOrderForm(instance=order)
        item_formset = ItemFormSet(queryset=PurchaseOrderItem.objects.filter(purchaseorder=order))

    return render(request, 'purchaseorder/purchaseorder_form_partial.html', {
        'order_form': order_form,
        'item_formset': item_formset,
        'order': order,
    })

def delete_purchase_order(request, order_id):
    # Obtener y eliminar la orden de compra
    order = get_object_or_404(PurchaseOrder, id=order_id)
    order.delete()
    
    # Retornar un mensaje simple en HTML
    return HttpResponse('<div class="alert alert-success">Orden de compra eliminada con éxito. Si quieres crear una orden nueva, tendrás que hacerlo desde el pedido.</div>', content_type="text/html")

# Bank 
def index_bank(request):
    if request.method == 'POST':
        form = BankForm(request.POST)  
        if form.is_valid():
            print("Formulario válido. Banco:", form.cleaned_data.get('bank_name'))
            form.save()

            if request.headers.get('HX-Request'):  # Si es una petición HTMX
                context = {'banks': Bank.objects.all().order_by('-id')}
                return render(request, 'bank/bank_list.html', context)

            context = {'form': BankForm(), 'banks': Bank.objects.all()}
            return render(request, 'bank/bank_index.html', context)

        if request.headers.get('HX-Request'):  # Manejar los errores en HTMX
            return HttpResponse("Error en el formulario", status=400)

        return render(request, 'client/partials/failure_client.html')

    # En caso de GET request, mostrar el formulario vacío y la lista de bancos
    form = BankForm()
    context = {
        'form': form,
        'banks': Bank.objects.all().order_by('-id'),
        'pagina_activa': 'bancos'
    }
    return render(request, 'bank/bank_index.html', context)

def edit_bank(request, bank_id):
    bank = get_object_or_404(Bank, id=bank_id)
    
    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            bank = form.save()

            if request.headers.get('HX-Request'): 
                banks = Bank.objects.all().order_by('-id')
                return render(request, 'bank/bank_list.html', {'bank': bank, 'banks': banks})

            return redirect('bank_index')  

        if request.headers.get('HX-Request'):  # Manejar los errores en HTMX
            return HttpResponse("Error en el formulario", status=400)

        return render(request, 'client/partials/failure_client.html')

    # Corregir aquí asegurándonos de pasar el objeto `bank` al contexto
    form = BankForm(instance=bank)
    banks = Bank.objects.all().order_by('-id')  
    context = {
        'form': form,
        'banks': banks,
        'bank': bank 
    }
    return render(request, 'bank/bank_edit.html', context)

# Bank Delete
def delete_bank(request, bank_id):
    bank = get_object_or_404(Bank, id=bank_id)
    
    if request.method == 'POST':
        bank.delete()

        if request.headers.get('HX-Request'):  # Si es una petición HTMX
            return HttpResponse(status=204)

        return redirect('bank_index')  # Redirigir después de eliminar

    return render(request, 'bank/bank_delete.html', {'bank': bank})

# BankStatements
def bank_statements(request, bank_id):
    bank = get_object_or_404(Bank, pk=bank_id)
    statements = BankStatements.objects.filter(bank=bank)
    return render(request, 'bankstatement/BankStatements_list.html', {'bank': bank, 'statements': statements})

class BankStatementUploadView(FormView):
    template_name = 'bankstatement/upload_bank_statements.html'
    form_class = UploadBankStatementForm
    success_url = reverse_lazy('bank_index')

    def form_valid(self, form):
        bank = form.cleaned_data['bank']
        bank_name = bank.bank_name.strip()
        uploaded_file = self.request.FILES['excel_file']

        try:
            # Leer todas las hojas del archivo Excel
            sheets = pd.read_excel(uploaded_file, sheet_name=None, engine='openpyxl', header=2)
            print("Nombres de hojas en el archivo:", sheets.keys())

            # Verificar si el nombre del banco coincide con alguna hoja
            if bank_name in sheets:
                df = sheets[bank_name]
                print("Columnas en la hoja antes de ajustar:", df.columns)

                # Renombrar columnas para que coincidan con los campos del modelo
                column_mapping = {
                    'F.Operac.': 'operation_date',
                    'Referencia': 'reference',
                    'Importe': 'amount',
                    'ITF': 'itf',
                    'Num.Mvto': 'number_moviment',
                }
                df.rename(columns=column_mapping, inplace=True)

                # Filtrar columnas necesarias
                df = df[['operation_date', 'reference', 'amount', 'itf', 'number_moviment']]
                print("Columnas en la hoja después de ajustar:", df.columns)

                # Eliminar filas con valores vacíos en las columnas clave
                initial_count = len(df)
                df.dropna(subset=['operation_date', 'reference', 'amount', 'number_moviment'], inplace=True)
                print(f"Total de filas antes de filtrar vacíos: {initial_count}, después: {len(df)}")

                # Procesar cada fila
                for _, row in df.iterrows():
                    try:
                        # Convertir la fecha utilizando pd.to_datetime()
                        operation_date = pd.to_datetime(row['operation_date']).date()
                    except Exception as e:
                        messages.warning(self.request, f"Fecha inválida en número de movimiento {row['number_moviment']}: {row['operation_date']}")
                        continue  # Saltar a la siguiente fila en caso de error

                    # Evitar duplicados
                    if not BankStatements.objects.filter(
                        bank=bank,
                        operation_date=operation_date,
                        number_moviment=row['number_moviment']
                    ).exists():
                        # Crear registro
                        BankStatements.objects.create(
                            bank=bank,
                            operation_date=operation_date,
                            reference=row['reference'],
                            amount=row['amount'],
                            itf=row['itf'],
                            number_moviment=row['number_moviment']
                        )
                    else:
                        print(f"Registro duplicado encontrado para número de movimiento: {row['number_moviment']}")

                # Mensaje de éxito
                messages.success(self.request, f'Extractos bancarios para {bank_name} subidos exitosamente.')
            else:
                messages.error(self.request, f'No se encontró una hoja para el banco: {bank_name}.')

        except Exception as e:
            print("Error procesando archivo:", e)
            messages.error(self.request, f'Hubo un error procesando el archivo: {e}')

        return super().form_valid(form)

@require_POST
def assign_bank_statement(request, item_id, statement_id):
    try:
        # Obtener el ítem y el extracto bancario
        item = PurchaseOrderItem.objects.get(id=item_id)
        bank_statement = BankStatements.objects.get(id=statement_id)

        # Asignar el extracto bancario al ítem
        item.bank_statement = bank_statement
        item.mov_number = bank_statement.number_moviment
        item.save()

        return JsonResponse({'success': True, 'message': 'Conciliación realizada correctamente.'})
    except PurchaseOrderItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Ítem no encontrado.'})
    except BankStatements.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Extracto bancario no encontrado.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

# Bank loands and credit cards
def bank_loans(request):
    prestamo = BankLoan.objects.filter(credit_type = 'prestamo')
    credito = BankLoan.objects.filter(credit_type = 'credito')

    context = {
        'prestamos': prestamos,
        'creditos': creditos
    }

    return render(request, 'bank_loans.html', )

#caja chica
def petty_cash(request):
    # Obtener la fecha de hoy según la zona horaria configurada
    today = localdate()

    # Obtenemos los parámetros del rango de fechas (si existen)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Si no se han proporcionado fechas, mostrar ítems del día actual
    if not start_date and not end_date:
        items = PurchaseOrderItem.objects.filter(purchaseorder__scheduled_date=today).select_related(
            'purchaseorder', 'sales_order_item__salesorder', 'supplier'
        )
    else:
        # Si se proporcionan fechas, buscar entre esas dos fechas
        if not end_date:
            end_date = today  # Si solo hay fecha de inicio, el rango termina en el día actual

        items = PurchaseOrderItem.objects.filter(
            purchaseorder__scheduled_date__range=[start_date, end_date]
        ).select_related('purchaseorder', 'sales_order_item__salesorder', 'supplier')

    context = {
        'items': items,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'pettycash/petty_cash_items.html', context)

def petty_cash_state(request):
    # Obtener los parámetros de filtro
    payment_status = request.GET.get('status')  # Puede ser "Pagado" o "No Pagado"
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Inicializar el queryset base
    items = PurchaseOrderItem.objects.select_related(
        'purchaseorder', 'sales_order_item__salesorder', 'supplier'
    )

    # Filtrar por estado de pago si está definido
    if payment_status:
        items = items.filter(payment_status=payment_status)

    # Si no se filtra por estado de pago, aplicar el filtro de fechas
    elif start_date or end_date:
        if not end_date:
            end_date = localdate()  # Fecha actual como final si no se especifica
        if not start_date:
            start_date = localdate()  # Fecha actual como inicio si no se especifica

        items = items.filter(purchaseorder__scheduled_date__range=[start_date, end_date])

    context = {
        'items': items,
        'start_date': start_date,
        'end_date': end_date,
        'payment_status': payment_status,
        'class_pay_choices': PurchaseOrderItem.CLASS_PAY_CHOICES,
        'type_pay_choices': PurchaseOrderItem.TYPE_PAY_CHOICES,
    }
    return render(request, 'pettycash/petty_cash_state.html', context)

def update_payment_status(request, item_id):
    item = get_object_or_404(PurchaseOrderItem, id=item_id)
    item.payment_status = 'Pagado' if item.payment_status == 'No Pagado' else 'No Pagado'
    item.save()
    return JsonResponse({'status': item.payment_status})

@csrf_exempt
def update_field(request, item_id):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            field = data.get('field')
            value = data.get('value')

            item = get_object_or_404(PurchaseOrderItem, id=item_id)

            if field in ['class_pay', 'type_pay']:
                setattr(item, field, value)
                item.save()
                return JsonResponse({'success': True, 'field': field, 'value': value})

            return JsonResponse({'success': False, 'error': 'Campo no válido.'}, status=400)

        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Import requirements views
class AccountingRequirementOrderListView(ListView):
    model = RequirementOrder
    template_name = 'requirements/requirement_order_list.html'
    context_object_name = 'requirement_orders'

    def get_queryset(self):
        # Obtiene el parámetro "filter" desde la URL
        filter_type = self.request.GET.get('filter', 'no_revisado')
        
        if filter_type == 'all':
            # Si el filtro es "all", retorna todas las órdenes
            return RequirementOrder.objects.all().order_by('-id').prefetch_related('items')
        else:
            # Por defecto muestra solo las órdenes "NO REVISADO"
            return RequirementOrder.objects.filter(state="NO REVISADO").order_by('-id').prefetch_related('items')

def accounting_requirement_order_detail_view(request, pk):
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)
    items = requirement_order.items.all()
    suppliers = Suppliers.objects.all()
    return render(request, 'requirements/requirement_order_detail.html', {
        'requirement_order': requirement_order,
        'items': items,
        'suppliers': suppliers,
    })

@require_POST
def update_requirement_order_items(request, pk):
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)
    updated_items = []

    new_state = request.POST.get('requirement_order_state')
    if new_state in dict(RequirementOrder.STATE_CHOICES):
        requirement_order.state = new_state
        
    # Recorrer los ítems de la orden y actualizar con los datos recibidos del request.POST
    for item in requirement_order.items.all():
        item.quantity_requested = request.POST.get(f'quantity_requested_{item.id}', item.quantity_requested)
        item.price = request.POST.get(f'price_{item.id}', item.price)
        item.notes = request.POST.get(f'notes_{item.id}', item.notes)
        item.supplier_id = request.POST.get(f'supplier_{item.id}')
        item.estado = request.POST.get(f'estado_{item.id}', item.estado)
        item.save()
        updated_items.append(item)
    
    requirement_order.save()

    return JsonResponse({'message': 'Elementos actualizados con éxito'}, status=200)

def create_purchase_order(request, pk):
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)

    # Verificar si ya existe una orden de compra para esta orden de requerimiento
    if requirement_order.purchase_order_created:
        error_message = "<div>Ya se se ha creado una Orden de Compra para esta Orden de Requerimiento.</div>"
        return HttpResponse(error_message, content_type="text/html")

    # Filtrar los ítems que están en estado "C"
    items_comprando = RequirementOrderItem.objects.filter(requirement_order=requirement_order, estado='C')
    
    if not items_comprando.exists():
        error_message = "<div>No hay ítems en estado 'Comprando' para crear una Orden de Compra.</div>"
        return HttpResponse(error_message, content_type="text/html")

    # Crear la PurchaseOrder
    with transaction.atomic():
        purchase_order = PurchaseOrder.objects.create(
            salesorder=requirement_order.sales_order,
            description=f"{requirement_order.notes} - {requirement_order.order_number}",
            requested_date=requirement_order.requested_date,
            requested_by=request.user.username if request.user else 'Desconocido',
            acepted=True
        )

        # Crear los PurchaseOrderItems asociados a los ítems comprando
        purchase_order_items = [
            PurchaseOrderItem(
                purchaseorder=purchase_order,
                sales_order_item=item.sales_order_item,
                sap_code=item.sap_code,
                quantity_requested=item.quantity_requested,
                price=item.price,
                price_total=item.total_price,
                notes=item.notes,
                supplier=item.supplier
            )
            for item in items_comprando
        ]
        PurchaseOrderItem.objects.bulk_create(purchase_order_items)

        # Actualizar la RequirementOrder para indicar que la orden de compra ha sido creada
        requirement_order.purchase_order_created = True
        requirement_order.save()

    # Respuesta de éxito en HTML
    success_message = f"<div>Orden de Compra creada para la Orden de Requerimiento #{requirement_order.order_number}.</div>"
    return HttpResponse(success_message, content_type="text/html")

#APROBAR REQUERIMIENTOS:
@require_POST
def update_requirement_order_state(request, pk):
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)
    new_state = request.POST.get('state')

    if new_state in dict(RequirementOrder.STATE_CHOICES):
        requirement_order.state = new_state
        requirement_order.save()
        # Mensaje de éxito
        message = 'La orden ha sido aprobada con éxito.' if new_state == 'APROBADO' else 'La orden ha sido rechazada con éxito.'
        response_content = f"<div>{message}</div>"
        return HttpResponse(response_content, content_type="text/html")
    else:
        # Mensaje de error
        error_message = "<div>Estado inválido. Por favor, selecciona un estado válido.</div>"
        return HttpResponse(error_message, content_type="text/html")

def ajax_load_suppliers(request):
    term = request.GET.get('term', '')
    suppliers = Suppliers.objects.filter(name__icontains=term)[:20]
    supplier_list = [{'id': supplier.id, 'text': supplier.name} for supplier in suppliers]
    return JsonResponse({'results': supplier_list})

def purchase_conciliations(request):
    # Obtener los parámetros de fecha y nombre del banco
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    bank_name = request.GET.get('bank_name', '').strip()  # Tomar el nombre del banco o cadena vacía si no hay

    # Inicializar `items` y `bank_statements` como listas vacías para que la página cargue sin datos
    items = PurchaseOrderItem.objects.none()
    bank_statements = BankStatements.objects.none()

    # Solo aplicar filtros si se proporcionan `start_date`, `end_date`, o `bank_name`
    if start_date or end_date or bank_name:
        # Asignar valores por defecto si las fechas están vacías
        start_date = start_date or localdate()
        end_date = end_date or localdate()

        # Filtro para ítems sin número de movimiento y coincidencias en el nombre del banco
        items = PurchaseOrderItem.objects.filter(
                purchaseorder__scheduled_date__range=[start_date, end_date]
            ).filter(
                Q(mov_number__isnull=True) | Q(mov_number=''),  # Solo ítems sin número de movimiento
                supplier__bank__icontains=bank_name  # Coincidencia parcial en el nombre del banco del proveedor
            ).select_related('purchaseorder', 'sales_order_item__salesorder', 'supplier')

        # Filtro para los extractos bancarios por fecha y nombre del banco
        bank_statements = BankStatements.objects.filter(
            operation_date__range=[start_date, end_date],
            bank__bank_name__icontains=bank_name  # Coincidencia parcial en el nombre del banco de los extractos
        )

    context = {
        'items': items,
        'bank_statements': bank_statements,
        'start_date': start_date,
        'end_date': end_date,
        'bank_name': bank_name,
    }

    return render(request, 'conciliations/conciliations.html', context)

def report_conciliations(request):
    # Obtener el banco seleccionado desde el formulario
    selected_bank_id = request.GET.get('bank_id')
    selected_bank = None
    bank_statements = []

    # Obtener todos los bancos para el selector
    banks = Bank.objects.all()

    # Si se selecciona un banco, filtrar sus extractos
    if selected_bank_id:
        selected_bank = Bank.objects.filter(id=selected_bank_id).first()
        if selected_bank:
            # Obtener los extractos y las órdenes relacionadas
            bank_statements = BankStatements.objects.filter(bank=selected_bank).prefetch_related(
                Prefetch(
                    'conciliated_items',  # Relación definida en `PurchaseOrderItem`
                    queryset=PurchaseOrderItem.objects.select_related('purchaseorder', 'supplier'),
                )
            )

    context = {
        'banks': banks,
        'selected_bank': selected_bank,
        'bank_statements': bank_statements,
    }

    return render(request, 'conciliations/report_conciliations.html', context)

# renditions
def purchase_renditions(request):
    today = localdate()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date and not end_date:
        items = PurchaseOrderItem.objects.filter(purchaseorder__scheduled_date=today).select_related(
            'purchaseorder', 'sales_order_item__salesorder', 'supplier'
        )
    else:
        if not end_date:
            end_date = today

        items = PurchaseOrderItem.objects.filter(
            purchaseorder__scheduled_date__range=[start_date, end_date]
        ).select_related('purchaseorder', 'sales_order_item__salesorder', 'supplier')

    # Calcular el total restante para cada item
    for item in items:
        total_renditions = item.renditions.aggregate(total=Sum('amount'))['total'] or 0
        item.total_remaining = item.price_total - total_renditions if item.price_total else 0

    context = {
        'items': items,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'renditions/renditions.html', context)

@require_POST
def add_rendition(request):
    # Extraer los datos del formulario
    item_id = request.POST.get('item_id')
    amount = request.POST.get('amount')
    series = request.POST.get('series')  # Obtener la serie del formulario
    correlative = request.POST.get('correlative')  # Obtener el correlativo del formulario
    date = request.POST.get('date') 
    photo = request.FILES.get('photo')


    # Obtener el ítem o devolver un error 404 si no existe
    item = get_object_or_404(PurchaseOrderItem, id=item_id)

    try:
        # Crear la rendición con los datos recibidos
        rendition = Rendition(
            purchase_order_item=item,
            amount=amount,
            series=series,  # Guardar la serie
            correlative=correlative,  # Guardar el correlativo
            date=date if date else None,
            photo=photo,

        )

        # Intentar guardar la rendición
        rendition.save()

        # Si todo va bien, devolver un mensaje de éxito
        return JsonResponse({'status': 'success', 'message': 'Rendición añadida correctamente'})

    except ValidationError as e:
        # Captura el error y envía el primer mensaje de error de la lista
        return JsonResponse({'status': 'error', 'message': str(e.message or e.messages[0])})

# Listar órdenes de cobro y procesar carga de PDF
def collection_orders(request):
    if request.method == "POST":
        salesorder_id = request.POST.get("salesorder_id")
        pdf_file = request.FILES.get("pdf_file")

        if pdf_file and salesorder_id:
            orden_venta = get_object_or_404(SalesOrder, pk=salesorder_id)
            datos_pdf = extraer_datos_pdf(pdf_file)

            # Crear instancia de CollectionOrders con los datos extraídos
            collection_order = CollectionOrders(
                orden_venta=orden_venta,
                serie_correlativo=datos_pdf["serie_correlativo"],
                fecha_emision=datos_pdf["fecha_emision"],
                cliente=datos_pdf["cliente"],
                ruc_cliente=datos_pdf["ruc_cliente"],
                tipo_moneda=datos_pdf["tipo_moneda"],
                descripcion=datos_pdf["descripcion"],
                importe_total=datos_pdf["importe_total"],
                detraccion=datos_pdf["detraccion"],
                monto_neto_cobrar=datos_pdf["monto_neto_cobrar"],
                total_cuotas=datos_pdf["total_cuotas"],
                fecha_vencimiento=datos_pdf["fecha_vencimiento"],
            )
            collection_order.save()
            messages.success(request, "PDF procesado y datos guardados exitosamente.")

    # Obtener todas las SalesOrder para listarlas en la página
    sales_orders = SalesOrder.objects.all()
    context = {
        'sales_orders': sales_orders,
    }
    return render(request, 'collectionorders/collection_orders.html', context)

def collection_order_detail(request, salesorder_id):
    # Obtiene la SalesOrder y sus CollectionOrders asociadas
    orden_venta = get_object_or_404(SalesOrder, pk=salesorder_id)
    collection_orders = CollectionOrders.objects.filter(orden_venta=orden_venta)

    # Procesa el PDF si se carga uno
    if request.method == "POST":
        pdf_file = request.FILES.get("pdf_file")

        if pdf_file:
            datos_pdf = extraer_datos_pdf(pdf_file)

            # Crear una nueva instancia de CollectionOrders con los datos extraídos
            collection_order = CollectionOrders(
                orden_venta=orden_venta,
                serie_correlativo=datos_pdf["serie_correlativo"],
                fecha_emision=datos_pdf["fecha_emision"],
                cliente=datos_pdf["cliente"],
                ruc_cliente=datos_pdf["ruc_cliente"],
                tipo_moneda=datos_pdf["tipo_moneda"],
                descripcion=datos_pdf["descripcion"],
                importe_total=datos_pdf["importe_total"],
                detraccion=datos_pdf["detraccion"],
                monto_neto_cobrar=datos_pdf["monto_neto_cobrar"],
                total_cuotas=datos_pdf["total_cuotas"],
                fecha_vencimiento=datos_pdf["fecha_vencimiento"],
            )
            collection_order.save()
            messages.success(request, "PDF procesado y datos guardados exitosamente.")
            return redirect('collection_order_detail', salesorder_id=salesorder_id)

    context = {
        'orden_venta': orden_venta,
        'collection_orders': collection_orders,
    }
    return render(request, 'collectionorders/collection_order_detail.html', context)

# Eliminar una orden de cobro
def delete_collection_order(request, collection_order_id):
    collection_order = get_object_or_404(CollectionOrders, pk=collection_order_id)
    salesorder_id = collection_order.orden_venta.id
    collection_order.delete()
    return redirect(reverse('collection_orders', kwargs={'salesorder_id': salesorder_id}))

# Editar una orden de cobro
def edit_collection_order(request, collection_order_id):
    collection_order = get_object_or_404(CollectionOrders, pk=collection_order_id)
    
    if request.method == 'POST':
        form = CollectionOrdersForm(request.POST, instance=collection_order)
        if form.is_valid():
            form.save()
            return redirect(reverse('collection_orders', kwargs={'salesorder_id': collection_order.orden_venta.id}))
    else:
        form = CollectionOrdersForm(instance=collection_order)
    
    context = {
        'form': form,
        'collection_order': collection_order,
    }
    
    return render(request, 'collectionorders/edit_collection_order.html', context)















