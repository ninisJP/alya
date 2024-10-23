from django.shortcuts import render, get_object_or_404
from .forms import RequirementOrderForm, RequirementOrderItemFormSet
from django.shortcuts import render
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


# # Vista para listar todas las RequirementOrders
class RequirementOrderListView(ListView):
    model = RequirementOrder
    template_name = 'requirement_order_list.html'
    context_object_name = 'requirement_orders'

    def get_queryset(self):
        queryset = RequirementOrder.objects.all().order_by('-id').prefetch_related('items')
        
        for order in queryset:
            items = order.items.all()
            total_items = items.count()
            if total_items == 0:
                order.global_state = "No tiene ítems"
                continue

            ready_count = items.filter(estado='L').count()
            buying_count = items.filter(estado='C').count()

            # Determinar el estado general
            if ready_count == total_items:
                order.global_state = "Listo"
            elif buying_count >= total_items / 2:
                order.global_state = "Comprando"
            else:
                order.global_state = "Pendiente"
                
        return queryset

    
def requirement_order_detail_view(request, pk):
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)
    items = requirement_order.items.all()
    suppliers = Suppliers.objects.all()
    return render(request, 'requirement_order_detail.html', {
        'requirement_order': requirement_order,
        'items': items,
        'suppliers': suppliers,
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

# Requirements order approved 

class RequirementOrderApprovedListView(ListView):
    model = RequirementOrder
    template_name = 'requirements_approved/requirement_order_approved_list.html'
    context_object_name = 'requirement_orders'

    def get_queryset(self):
        queryset = RequirementOrder.objects.all().order_by('-id').prefetch_related('items')
        
        for order in queryset:
            items = order.items.all()
            total_items = items.count()
            if total_items == 0:
                order.global_state = "No tiene ítems"
                continue

            ready_count = items.filter(estado='L').count()
            buying_count = items.filter(estado='C').count()

            # Determinar el estado general
            if ready_count == total_items:
                order.global_state = "Listo"
            elif buying_count >= total_items / 2:
                order.global_state = "Comprando"
            else:
                order.global_state = "Pendiente"
                
        return queryset