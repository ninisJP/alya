from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from accounting_order_sales.models import SalesOrder, SalesOrderItem
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from .forms import CreateRequirementOrderForm, CreateRequirementOrderItemFormSet 
from django.views.generic import DetailView
from django.forms import inlineformset_factory
from .forms import CreateRequirementOrderForm, CreateRequirementOrderItemForm, CreateRequirementOrderItemFormSet
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import CreateRequirementOrderForm, PrepopulatedRequirementOrderItemForm
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from logistic_suppliers.models import Suppliers

def index_requests(request):
    sales_orders = SalesOrder.objects.all().order_by('-id')
    return render(request, 'index_requests.html', {'sales_orders': sales_orders})

def my_requests(request):
    my_orders = RequirementOrder.objects.filter(user=request.user).order_by('-id')
    return render(request, 'requests/my_requests.html', {'my_orders': my_orders})

def delete_order(request, order_id):
    if request.method == 'DELETE':
        order = get_object_or_404(RequirementOrder, id=order_id, user=request.user)
        order.delete()
        # Aquí devolvemos un fragmento HTML directamente
        return HttpResponse('<div class="alert alert-success">¡El pedido ha sido eliminado correctamente!</div>', content_type='text/html')
    return HttpResponse('<div class="alert alert-danger">Hubo un problema al eliminar el pedido.</div>', status=400)

def create_requests(request, order_id):
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    referencia_ordenventa = SalesOrderItem.objects.filter(salesorder=sales_order)

    if request.method == "POST":
        order_form = CreateRequirementOrderForm(request.POST)
        formset = CreateRequirementOrderItemFormSet(request.POST, request.FILES, form_kwargs={'sales_order': sales_order})

        if order_form.is_valid() and formset.is_valid():
            try:
                requirement_order = order_form.save(commit=False)
                requirement_order.sales_order = sales_order
                requirement_order.user = request.user
                requirement_order.save()

                items = formset.save(commit=False)
                for item in items:
                    item.requirement_order = requirement_order
                    item.price = item.price or item.sales_order_item.price
                    
                    try:
                        item.clean()
                        item.save()
                    except ValidationError as e:
                        item_name = item.sales_order_item.description
                        for message in e.messages:
                            messages.error(request, f"Error en el ítem '{item_name}': {message}")

                messages.success(request, "Pedido creado exitosamente.")
                return redirect('index_requests')

            except ValidationError as e:
                messages.error(request, str(e))
        else:
            for form in formset:
                if form.errors:
                    item_name = form.cleaned_data.get('sales_order_item', 'Sin nombre')
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"Error en {item_name}: {field} - {error}")
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        order_form = CreateRequirementOrderForm(initial={'sales_order': sales_order})
        formset = CreateRequirementOrderItemFormSet(
            queryset=RequirementOrderItem.objects.none(),
            form_kwargs={'sales_order': sales_order}
        )

    return render(request, 'requests/create_requests.html', {
        'order_form': order_form,
        'formset': formset,
        'sales_order': sales_order,
        'referencia_ordenventa': referencia_ordenventa
    })

def create_prepopulated_request(request, order_id):
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    sales_order_items = SalesOrderItem.objects.filter(salesorder=sales_order)

    # Prepare initial data
    initial_items = [
        {
            'sales_order_item': item.id,
            'quantity_requested': item.amount,
        }
        for item in sales_order_items
    ]

    PrepopulatedFormSet = inlineformset_factory(
        RequirementOrder,
        RequirementOrderItem,
        form=PrepopulatedRequirementOrderItemForm,
        extra=len(initial_items),
        can_delete=True  # Allow users to delete items
    )

    if request.method == "POST":
        order_form = CreateRequirementOrderForm(request.POST)
        formset = PrepopulatedFormSet(
            request.POST,
            form_kwargs={'sales_order': sales_order}
        )

        if order_form.is_valid() and formset.is_valid():
            try:
                requirement_order = order_form.save(commit=False)
                requirement_order.sales_order = sales_order
                requirement_order.user = request.user
                requirement_order.save()

                items = formset.save(commit=False)
                for item in items:
                    item.requirement_order = requirement_order
                    item.save()

                messages.success(request, "Pedido creado exitosamente.")
                return redirect('index_requests')

            except ValidationError as e:
                messages.error(request, str(e))
        else:
            # Display errors for debugging
            print("Order form errors:", order_form.errors)
            print("Formset errors:", formset.errors)
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        order_form = CreateRequirementOrderForm(initial={'sales_order': sales_order})
        formset = PrepopulatedFormSet(
            queryset=RequirementOrderItem.objects.none(),
            initial=initial_items,
            form_kwargs={'sales_order': sales_order}
        )

    # Attach item descriptions to each form
    for form, item in zip(formset.forms, sales_order_items):
        form.item_description = item.description

    # Crear lista combinada para pasar a la plantilla
    combined_data = [
        {
            'form': form,
            'unit_of_measurement': item.unit_of_measurement,
            'price': item.price,
            'price_total': item.price_total,
        }
        for form, item in zip(formset.forms, sales_order_items)
    ]

    return render(request, 'requests/create_prepopulated_request.html', {
        'order_form': order_form,
        'formset': formset,
        'sales_order': sales_order,
        'combined_data': combined_data,  # Lista combinada para la plantilla
    })



class MyRequestDetail(DetailView):
    model = RequirementOrder
    template_name = 'requests/my_request_detail.html'
    context_object_name = 'order'   
    
def delete_requirement_order_item(request, item_id):
    # Obtener el item a eliminar y su RequirementOrder asociado
    item = get_object_or_404(RequirementOrderItem, id=item_id)
    order = item.requirement_order
    
    # Eliminar el item
    item.delete()
    
    # Re-renderizar el partial `items_table.html` con la lista de ítems actualizada
    return render(request, 'partials/item_table.html', {'order': order})
    
def ajax_load_suppliers(request):
    term = request.GET.get('term', '')  # Filtrar por nombre
    suppliers = Suppliers.objects.filter(name__icontains=term)[:20]
    supplier_list = [{'id': supplier.id, 'text': supplier.name} for supplier in suppliers]
    return JsonResponse({'results': supplier_list})  
    
# Nueva vista para pedidos rapidos 
def RequestSalesOrder(request, pk):
    # Obtener la SalesOrder específica y sus ítems asociados
    sales_order = get_object_or_404(SalesOrder, id=pk)
    
    # Prefetch para cargar los ítems con su información
    sales_order_items = sales_order.items.all().prefetch_related('requirementorderitem_set')
    
    # Obtener todos los proveedores para el select
    suppliers = Suppliers.objects.all()
    
    context = {
        'sales_order': sales_order,
        'sales_order_items': sales_order_items,
        'suppliers': suppliers,
    }
    return render(request, 'requests_plus/requests_plus.html', context)

@require_POST
def create_requirement_order(request, order_id):
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    
    order_has_errors = False
    items_to_create = []  # Lista para almacenar ítems válidos

    for item_id, quantity_requested in request.POST.items():
        if item_id.startswith("items-") and "-quantity_requested" in item_id:
            sales_order_item_id = int(item_id.split("-")[1])
            sales_order_item = get_object_or_404(SalesOrderItem, id=sales_order_item_id)

            try:
                quantity_requested = int(quantity_requested)
            except ValueError:
                messages.error(request, f"Cantidad solicitada inválida para el ítem {sales_order_item.description}. Debe ser un número entero.")
                order_has_errors = True
                continue

            price = request.POST.get(f"items-{sales_order_item_id}-price", sales_order_item.price)
            try:
                price = float(price)
            except ValueError:
                messages.error(request, f"Precio inválido para el ítem {sales_order_item.description}. Debe ser un número decimal.")
                order_has_errors = True
                continue

            if quantity_requested > sales_order_item.remaining_requirement:
                messages.error(request, f"La cantidad solicitada ({quantity_requested}) para el ítem '{sales_order_item.description}' excede la cantidad disponible ({sales_order_item.remaining_requirement}).")
                order_has_errors = True
                continue

            supplier_id = request.POST.get(f"items-{sales_order_item_id}-supplier")
            notes = request.POST.get(f"items-{sales_order_item_id}-notes", "")
            file_attachment = request.FILES.get(f"items-{sales_order_item_id}-file_attachment")

            items_to_create.append({
                "sales_order_item": sales_order_item,
                "quantity_requested": quantity_requested,
                "price": price,
                "notes": notes,
                "file_attachment": file_attachment,
                "supplier": Suppliers.objects.get(id=supplier_id) if supplier_id else None
            })

    if not items_to_create:
        return JsonResponse({"message": "Error: No se puede crear una orden de requerimiento sin ítems válidos.", "type": "error"}, status=400)

    requirement_order = RequirementOrder(
        sales_order=sales_order,
        user=request.user,
        requested_date=request.POST.get("requested_date"),
        notes=request.POST.get("notes")
    )
    requirement_order.save()

    for item_data in items_to_create:
        item = RequirementOrderItem(
            requirement_order=requirement_order,
            sales_order_item=item_data["sales_order_item"],
            quantity_requested=item_data["quantity_requested"],
            price=item_data["price"],
            notes=item_data["notes"],
            file_attachment=item_data["file_attachment"],
            supplier=item_data["supplier"]
        )
        item.save()

    return JsonResponse({"message": "Orden de Requerimiento creada exitosamente.", "type": "success"})
