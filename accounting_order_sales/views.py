import traceback
from django.forms import ValidationError, modelformset_factory
from django.shortcuts import render
from logistic_suppliers.models import Suppliers
from .models import SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem,Bank,BankStatements, Rendition
from .utils import procesar_archivo_excel
from .forms import PurchaseOrderForm, PurchaseOrderItemForm, SalesOrderForm, ItemSalesOrderExcelForm, ItemSalesOrderForm, BankForm,UploadBankStatementForm
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
import pandas as pd
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from django.utils.timezone import localdate
from django.db.models import Sum
from .models import BankStatements

# libs accounting
from django.shortcuts import render, redirect, get_object_or_404
from logistic_requirements.forms import RequirementOrderForm, RequirementOrderItemFormSet
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from accounting_order_sales.models import PurchaseOrder, PurchaseOrderItem
from django.db import transaction
from logistic_suppliers.models import Suppliers
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from django.views.decorators.http import require_POST
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from django.http import JsonResponse
from logistic_suppliers.models import Suppliers  # Ajusta según la ubicación de tu modelo
from alya.utils import send_state_change_email

# -----------------------------

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

from datetime import datetime

class BankStatementUploadView(FormView):
    template_name = 'bankstatement/upload_bank_statements.html'
    form_class = UploadBankStatementForm
    success_url = reverse_lazy('bank_index')

    def form_valid(self, form):
        # Obtener el banco seleccionado del formulario
        bank = form.cleaned_data['bank']
        uploaded_file = self.request.FILES['excel_file']

        try:
            # Leer el archivo como Excel
            if uploaded_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                raise ValueError("Formato de archivo no soportado.")

            # Mapeo de nombres de columnas
            column_mapping = {
                'F.Operac.': 'operation_date',
                'Referencia': 'reference',
                'Importe': 'amount',
                'ITF': 'itf',
                'Num.Mvto': 'number_moviment',
            }

            # Renombrar columnas
            df.rename(columns=column_mapping, inplace=True)

            # Crear los registros de BankStatements
            for _, row in df.iterrows():
                # Verifica si el banco está asignado
                if bank:
                    BankStatements.objects.create(
                        bank=bank,  # Asegúrate de que el banco se pase aquí
                        operation_date=row['operation_date'],
                        reference=row['reference'],
                        amount=row['amount'],
                        itf=row['itf'],
                        number_moviment=row['number_moviment'],
                    )
                else:
                    print("El banco no está asignado correctamente.")

            messages.success(self.request, 'Extractos bancarios subidos exitosamente.')
        except Exception as e:
            print("Error procesando archivo:", e)
            messages.error(self.request, 'Hubo un error procesando el archivo.')

        return super().form_valid(form)



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

# Import requirements views
 
# Vista para listar todas las RequirementOrders
class AccountingRequirementOrderListView(ListView):
    model = RequirementOrder
    template_name = 'requirements/requirement_order_list.html'
    context_object_name = 'requirement_orders'

    def get_queryset(self):
        return RequirementOrder.objects.all().order_by('-id')
    
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

    # Retornar un mensaje de éxito sin crear la PurchaseOrder
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

        # Enviar correo de notificación
        send_state_change_email(requirement_order)

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

# conciliations
def purchase_conciliations(request):
    # Obtener la fecha de hoy según la zona horaria configurada
    today = localdate()

    # Obtenemos los parámetros del rango de fechas (si existen)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Si no se han proporcionado fechas, mostrar ítems y movimientos del día actual
    if not start_date and not end_date:
        items = PurchaseOrderItem.objects.filter(purchaseorder__scheduled_date=today).select_related(
            'purchaseorder', 'sales_order_item__salesorder', 'supplier'
        )
        bank_statements = BankStatements.objects.filter(operation_date=today)
    else:
        # Si se proporcionan fechas, buscar entre esas dos fechas
        if not end_date:
            end_date = today  # Si solo hay fecha de inicio, el rango termina en el día actual

        items = PurchaseOrderItem.objects.filter(
            purchaseorder__scheduled_date__range=[start_date, end_date]
        ).select_related('purchaseorder', 'sales_order_item__salesorder', 'supplier')
        
        bank_statements = BankStatements.objects.filter(
            operation_date__range=[start_date, end_date]
        )

    context = {
        'items': items,
        'bank_statements': bank_statements,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'conciliations/conciliations.html', context)


# renditions
from django.db.models import Sum
from django.utils.timezone import localdate

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


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import PurchaseOrderItem

from django.core.exceptions import ValidationError

from django.core.exceptions import ValidationError

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

















