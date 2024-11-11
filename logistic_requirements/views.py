from django.shortcuts import render, get_object_or_404

from logistic_inventory.models import Item
from .forms import RequirementOrderForm, RequirementOrderItemFormSet
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from .models import RequirementOrder, RequirementOrderItem
from accounting_order_sales.models import PurchaseOrder, PurchaseOrderItem
from django.db import transaction
from logistic_suppliers.models import Suppliers
from django.http import JsonResponse
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import RequirementOrder, RequirementOrderItem
from django.http import HttpResponse
from django.db.models import Q

# Vista para listar todas las RequirementOrders aprobadas con ítems en estado Pendiente o todas las órdenes sin filtros
class RequirementOrderListView(ListView):
    model = RequirementOrder
    template_name = 'requirement_order_list.html'
    context_object_name = 'requirement_orders'

    def get_queryset(self):
        # Revisar si el parámetro GET "show_all" está presente
        show_all = self.request.GET.get('show_all') == 'true'
        
        if show_all:
            # Si show_all es true, retornar todas las órdenes sin filtros
            queryset = RequirementOrder.objects.all().order_by('-id').prefetch_related('items')
        else:
            # Filtrar solo órdenes aprobadas con al menos un ítem en estado Pendiente
            queryset = RequirementOrder.objects.filter(
                state='APROBADO',
                items__estado='P'
            ).distinct().order_by('-id').prefetch_related('items')
        
        # Calcular el estado general de cada orden
        for order in queryset:
            items = order.items.all()
            total_items = items.count()

            if total_items == 0:
                order.global_state = "No tiene ítems"
                continue

            ready_count = items.filter(estado='L').count()
            buying_count = items.filter(estado='C').count()
            pending_count = items.filter(estado='P').count()

            # Determinar el estado general
            if ready_count == total_items:
                order.global_state = "Listo"
            elif buying_count >= total_items / 2:
                order.global_state = "Comprando"
            elif pending_count > 0:
                order.global_state = "Pendiente"
            else:
                order.global_state = "Completado"  # Si no hay items pendientes, listos o comprando

        return queryset

def requirement_order_detail_view(request, pk):
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)
    filtrar = request.GET.get('filtrar')  # Se captura el parámetro sin valor por defecto

    # Filtrar los ítems en estado 'P' si se requiere, o cargar todos los ítems
    if filtrar == 'P':
        items = requirement_order.items.filter(estado='P').select_related('sales_order_item')
    else:
        items = requirement_order.items.all().select_related('sales_order_item')

    suppliers = Suppliers.objects.all()
    
    # Crear un diccionario de inventario disponible, usando sap como clave
    inventory_data = {item.item.sap: item.quantity for item in Item.objects.select_related('item').all()}
    
    # Agregar disponibilidad a cada item en el queryset
    for item in items:
        item.disponible_inventario = inventory_data.get(item.sap_code, 0)

    return render(request, 'requirement_order_detail.html', {
        'requirement_order': requirement_order,
        'items': items,
        'suppliers': suppliers,
        'filtrar': filtrar,  # Pasar el estado de filtro actual al template
    })

@require_POST
def update_requirement_order_items(request, pk):
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)
    updated_items = []
        
    # Recorrer los ítems de la orden y actualizar con los datos recibidos del request.POST
    for item in requirement_order.items.all():
        item.quantity_requested = request.POST.get(f'quantity_requested_{item.id}', item.quantity_requested)
        item.price = request.POST.get(f'price_{item.id}', item.price)
        item.notes = request.POST.get(f'notes_{item.id}', item.notes)
        item.supplier_id = request.POST.get(f'supplier_{item.id}')
        item.estado = request.POST.get(f'estado_{item.id}', item.estado)
        item.save()
        updated_items.append(item)
    
    # Retornar un mensaje de éxito sin crear la PurchaseOrder
    return JsonResponse({'message': 'Items actualizados con éxito'}, status=200)

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

def ajax_load_suppliers(request):
    term = request.GET.get('term', '')
    suppliers = Suppliers.objects.filter(name__icontains=term)[:20]
    supplier_list = [{'id': supplier.id, 'text': supplier.name} for supplier in suppliers]
    return JsonResponse({'results': supplier_list})

def requirement_order_approved_list(request):
    # Obtener los ítems cuyas órdenes de requerimiento están aprobadas y el estado del ítem es Pendiente
    requirement_order_items = RequirementOrderItem.objects.filter(
        requirement_order__state='APROBADO',
        estado='P'  # Filtro adicional para solo obtener los ítems en estado Pendiente
    ).select_related(
        'sales_order_item', 
        'sales_order_item__salesorder',
        'sales_order_item__salesorder__project',
        'supplier'
    ).order_by('-requirement_order__created_at')

    # Obtener la lista de proveedores
    suppliers = Suppliers.objects.all()

    # Pasar los ítems aprobados y pendientes, y los proveedores al contexto para ser utilizados en el template
    context = {
        'requirement_order_items': requirement_order_items,
        'suppliers': suppliers,
    }

    return render(request, 'requirements_approved/requirement_order_approved_list.html', context)


    
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import RequirementOrderItem

@require_POST
def update_approved_items(request):
    updated_items = []
    errors = []

    # Iterar sobre los datos POST
    for key, value in request.POST.items():
        try:
            # Validar que la clave tenga al menos 2 partes tras el split y que el segundo elemento sea un número
            parts = key.split('_')
            if len(parts) == 2 and parts[1].isdigit():
                # Obtener el ID del ítem desde el nombre del campo
                item_id = int(parts[1])

                # Obtener el ítem correspondiente de la base de datos
                try:
                    item = RequirementOrderItem.objects.get(id=item_id)
                except RequirementOrderItem.DoesNotExist:
                    errors.append(f"El ítem con ID {item_id} no existe.")
                    continue

                # Actualizar los campos según la clave
                if key.startswith('quantity_'):
                    try:
                        item.quantity_requested = int(value) if value else 0
                    except ValueError:
                        errors.append(f"Error al convertir la cantidad para el ítem {item_id}: {value}")
                        continue

                elif key.startswith('price_'):
                    try:
                        item.price = float(value) if value else 0.0
                    except ValueError:
                        errors.append(f"Error al convertir el precio para el ítem {item_id}: {value}")
                        continue

                elif key.startswith('notes_'):
                    item.notes = value

                elif key.startswith('supplier_'):
                    item.supplier_id = value

                elif key.startswith('estado_'):
                    item.estado = value

                # Guardar el ítem actualizado
                item.save()
                updated_items.append(item)
            else:
                # Si no tiene la estructura adecuada, añade un error
                errors.append(f"ID no válido: {parts[1] if len(parts) > 1 else 'desconocido'}")
        
        except Exception as e:
            errors.append(f"Error procesando el ítem: {str(e)}")
            continue

    # Si hubo errores, devolver un mensaje con los errores
    if errors:
        return JsonResponse({'message': 'Hubo errores al actualizar los ítems.', 'errors': errors}, status=400)
    """_summary_

    Returns:
        _type_: _description_
    """
    # Si todo fue bien, devolver solo un mensaje de éxito
    return JsonResponse({'message': 'Ítems actualizados con éxito'}, status=200)

def requirement_order_detail_partial(request, pk):
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)
    items = requirement_order.items.all() 
    return render(request, 'requirements_approved/requirement_order_detail_partial.html', {
        'requirement_order': requirement_order,
        'items': items,  # Pasamos los ítems a la plantilla parcial
    })

import openpyxl
from django.http import HttpResponse
from .models import RequirementOrder

def export_order_to_excel(request, pk):
    # Obtener la orden específica
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)
    # Filtrar solo los ítems en estado "Pendiente"
    items = requirement_order.items.filter(estado='P')
    
    # Crear un nuevo libro de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Orden {requirement_order.order_number}"

    # Encabezado con detalles de la orden
    ws['A1'] = "Detalles de la Orden"
    ws['A2'] = f"ID Orden: {requirement_order.order_number}"
    ws['A3'] = f"Proyecto: {requirement_order.sales_order.project.name}"
    ws['A4'] = f"Cliente: {requirement_order.sales_order.project.client.legal_name}"
    ws['A5'] = f"Fecha Solicitada: {requirement_order.requested_date}"
    ws['A6'] = f"Fecha Creada: {requirement_order.created_at}"
    ws['A7'] = f"Notas: {requirement_order.notes}"
    
    # Espacio entre detalles y tabla de ítems
    ws['A9'] = "Ítems Pendientes"

    # Agregar encabezados de columna para los ítems
    headers = ["Cantidad Solicitada", "Descripción", "Estado"]
    for col_num, column_title in enumerate(headers, 1):
        ws.cell(row=10, column=col_num, value=column_title)

    # Agregar los datos de cada ítem pendiente
    for row_num, item in enumerate(items, 11):  # Comienza en la fila 11 para dejar espacio a los detalles
        ws.cell(row=row_num, column=1, value=item.quantity_requested)
        ws.cell(row=row_num, column=2, value=item.sales_order_item.description)
        ws.cell(row=row_num, column=3, value=item.get_estado_display())

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="order_{requirement_order.order_number}_pending_items.xlsx"'
    wb.save(response)

    return response
