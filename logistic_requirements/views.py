from django.shortcuts import render, redirect, get_object_or_404
from .forms import RequirementOrderForm, RequirementOrderItemFormSet
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView 
from .models import RequirementOrder, RequirementOrderItem
from accounting_order_sales.models import PurchaseOrder, PurchaseOrderItem

# Vista para listar todas las RequirementOrders
class RequirementOrderListView(ListView):
    model = RequirementOrder
    template_name = 'requirement_order_list.html'
    context_object_name = 'requirement_orders'

def create_requirement_order(request):
    if request.method == "POST":
        order_form = RequirementOrderForm(request.POST)
        formset = RequirementOrderItemFormSet(request.POST)

        if order_form.is_valid() and formset.is_valid():
            requirement_order = order_form.save()  # Guardar la orden primero

            items = formset.save(commit=False)
            for item in items:
                item.requirement_order = requirement_order  # Asignar la orden a los ítems
                item.save()

            return redirect('requirement_order_list')
    else:
        order_form = RequirementOrderForm()
        formset = RequirementOrderItemFormSet()

    return render(request, 'create_requirement_order.html', {
        'order_form': order_form,
        'formset': formset
    })

def edit_requirement_order(request, pk):
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)

    if request.method == "POST":
        order_form = RequirementOrderForm(request.POST, instance=requirement_order)
        formset = RequirementOrderItemFormSet(request.POST, instance=requirement_order)

        if order_form.is_valid() and formset.is_valid():
            order_form.save()

            items = formset.save(commit=False)
            for item in items:
                item.save()

            # Verificar si ya se creó una PurchaseOrder para esta RequirementOrder
            if requirement_order.purchase_order_created:
                print(f"Ya se creó una PurchaseOrder para la RequirementOrder {requirement_order.order_number}. No se crearán más órdenes de compra.")
            else:
                # Crear una lista de los ítems que están en estado "C" (Comprando)
                items_comprando = RequirementOrderItem.objects.filter(requirement_order=requirement_order, estado='C')

                if items_comprando.exists():
                    # Crear la PurchaseOrder solo con los ítems que están en estado "C"
                    purchase_order = PurchaseOrder.objects.create(
                        salesorder=requirement_order.sales_order,
                        description=f"Purchase Order for {requirement_order.order_number}",
                        requested_date=requirement_order.requested_date,
                        requested_by=request.user.username if request.user else 'Desconocido',
                        acepted=True
                    )

                    # Crear PurchaseOrderItems para cada ítem en estado "C"
                    for item in items_comprando:
                        purchase_order_item = PurchaseOrderItem.objects.create(
                            purchaseorder=purchase_order,
                            sales_order_item=item.sales_order_item,
                            sap_code=item.sap_code,
                            quantity_requested=item.quantity_requested,
                            price=item.price,
                            price_total=item.total_price
                        )

                    # Marcar que ya se creó la PurchaseOrder
                    requirement_order.purchase_order_created = True
                    requirement_order.save()

                    print(f"PurchaseOrder creada: {purchase_order.description} para la SalesOrder {purchase_order.salesorder.sapcode}")
                    for item in items_comprando:
                        print(f"PurchaseOrderItem creado: {item.sales_order_item.description} (Cantidad: {item.quantity_requested}, Total: {item.total_price})")

            # Redirigir después de guardar
            return redirect('requirement_order_list')
        else:
            print(order_form.errors)
            print(formset.errors)
    else:
        order_form = RequirementOrderForm(instance=requirement_order)
        formset = RequirementOrderItemFormSet(instance=requirement_order)

    return render(request, 'requirements/edit_requirement_order.html', {
        'order_form': order_form,
        'formset': formset,
        'requirement_order': requirement_order
    })




