import traceback
from django.forms import ValidationError, modelformset_factory
from django.shortcuts import render

from logistic_suppliers.models import Suppliers
from .models import SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem
from .utils import procesar_archivo_excel
from .forms import PurchaseOrderForm, PurchaseOrderItemForm, SalesOrderForm, ItemSalesOrderExcelForm, ItemSalesOrderForm
from django.http import HttpResponse, HttpResponseServerError, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404

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
    purchase_orders = PurchaseOrder.objects.all() 
    context = {
        'purchase_orders': purchase_orders, 
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
        # Formulario para la orden de compra
        order_form = PurchaseOrderForm(request.POST, instance=order)
        # Formset para los ítems de la orden de compra
        item_formset = ItemFormSet(request.POST, queryset=PurchaseOrderItem.objects.filter(purchaseorder=order))

        if order_form.is_valid() and item_formset.is_valid():
            # Guardar la orden de compra y los ítems
            order_form.save()
            item_formset.save()

            # Después de guardar, devolver el artículo actualizado
            return render(request, 'purchaseorder/purchaseorder_partial.html', {'order': order})
    else:
        order_form = PurchaseOrderForm(instance=order)
        item_formset = ItemFormSet(queryset=PurchaseOrderItem.objects.filter(purchaseorder=order))

    return render(request, 'purchaseorder/purchaseorder_form_partial.html', {
        'order_form': order_form,
        'item_formset': item_formset,
        'order': order,
    })
    

#caja chica
def petty_cash(request):
    # Obtener todos los ítems de las órdenes de compra que tienen fecha de pago
    items = PurchaseOrderItem.objects.filter(purchaseorder__scheduled_date__isnull=False).select_related('purchaseorder', 'sales_order_item__salesorder', 'supplier')

    context = {
        'items': items,  # Pasamos todos los ítems de órdenes de compra
    }

    return render(request, 'pettycash/petty_cash_items.html', context)
