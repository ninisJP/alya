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
    # Obtener la orden de compra
    order = get_object_or_404(PurchaseOrder, id=order_id)

    # Crear el FormSet para los ítems de la orden de compra
    ItemFormSet = modelformset_factory(PurchaseOrderItem, form=PurchaseOrderItemForm, extra=0)

    if request.method == 'POST':
        # Recibir el order_id desde el formulario oculto
        order_id = request.POST.get('order_id')

        # Formulario para la orden de compra
        order_form = PurchaseOrderForm(request.POST, instance=order)

        # Formset para los ítems de la orden de compra
        item_formset = ItemFormSet(request.POST, queryset=PurchaseOrderItem.objects.filter(purchaseorder=order))

        if order_form.is_valid() and item_formset.is_valid():
            order_form.save()
            item_formset.save()

            # Después de guardar, recargar la lista de órdenes
            purchase_orders = PurchaseOrder.objects.filter(salesorder=order.salesorder)
            context = {
                'purchase_orders': purchase_orders,
                'order_id': order_id  # Asegúrate de pasar el order_id
            }

            return render(request, 'purchaseorder/purchaseorder_list_partial.html', context)
        else:
            # Si no son válidos, imprime los errores
            print("Errores del formulario de orden:", order_form.errors)
            print("Errores del formset de ítems:", item_formset.errors)

    else:
        # Cargar los formularios iniciales si no es POST
        order_form = PurchaseOrderForm(instance=order)
        item_formset = ItemFormSet(queryset=PurchaseOrderItem.objects.filter(purchaseorder=order))

    # Renderizar el formulario parcial con HTMX
    context = {
        'order_form': order_form,
        'item_formset': item_formset,
        'order': order,
        'order_id': order.id  # Asegúrate de pasar el order_id en el contexto
    }
    return render(request, 'purchaseorder/purchaseorder_form_partial.html', context)





def update_purchase_orders(request, item_id):
    # Obtener el PurchaseOrderItem por su ID
    item = get_object_or_404(PurchaseOrderItem, pk=item_id)

    # Campos que vamos a actualizar desde el formulario
    quantity_requested = request.POST.get("quantity_requested", "")
    price = request.POST.get("price", "")
    class_pay = request.POST.get("class_pay", "")
    type_pay = request.POST.get("type_pay", "")
    notes = request.POST.get("notes", "")
    supplier_id = request.POST.get("supplier", "")

    try:
        # Actualizar los campos en base a lo recibido en el formulario
        if quantity_requested:
            item.quantity_requested = int(quantity_requested)

        if price:
            item.price = round(float(price), 2)
            # Recalcular el precio total basado en la cantidad y el precio unitario
            item.price_total = round(item.quantity_requested * item.price, 2)

        if class_pay:
            item.class_pay = class_pay

        if type_pay:
            item.type_pay = type_pay

        if notes:
            item.notes = notes

        # Actualizar el proveedor solo si se envía uno válido
        if supplier_id:
            supplier = Suppliers.objects.filter(id=supplier_id).first()
            if supplier:
                item.supplier = supplier
            else:
                return HttpResponse("Proveedor no válido", status=400)

        # Guardar los cambios
        item.save()

        return HttpResponse(f"Actualización exitosa. Total: {item.price_total:.2f}")

    except ValueError:
        return HttpResponse("Error en los datos proporcionados", status=400)
    except ValidationError as e:
        return HttpResponse(f"Error de validación: {e.messages}", status=400)
    except Exception as e:
        return HttpResponse(f"Error inesperado: {str(e)}", status=500)
