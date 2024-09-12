from django.shortcuts import render
from .models import SalesOrder
from .forms import SalesOrderForm
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404

# Vista para listar y crear una orden de venta
def salesorder(request):
    salesorders = SalesOrder.objects.all().order_by("-id")
    context = {'form': SalesOrderForm(), 'salesorders': salesorders} 
    return render(request, 'salesorder/sales_index.html', context)

# Vista para crear una nueva orden de venta
def create_salesorder(request):
    if request.method == 'POST':
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            form.save()
            salesorders = SalesOrder.objects.all().order_by("-id")  # Asegúrate de que esté en plural
            context = {'salesorders': salesorders}
            return render(request, 'salesorder/salesorder-list.html', context)
    else:
        form = SalesOrderForm()
    return render(request, 'salesorder/salesorder-form.html', {'form': form})

# Vista para editar una orden de venta existente
def edit_salesorder(request, salesorder_id):
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    if request.method == 'GET':
        form = SalesOrderForm(instance=salesorder)
        return render(request, 'salesorder/edit-salesorder.html', {'form': form, 'salesorder': salesorder})
    elif request.method == 'POST':
        form = SalesOrderForm(request.POST, instance=salesorder)
        if form.is_valid():
            form.save()
            salesorders = SalesOrder.objects.all().order_by("-id")  # Plural para mantener consistencia
            return render(request, 'salesorder/salesorder-list.html', {'salesorders': salesorders})
    return HttpResponse(status=405)

# Vista para eliminar una orden de venta
def delete_salesorder(request, salesorder_id):
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    if request.method == 'DELETE':
        salesorder.delete()
        salesorders = SalesOrder.objects.all().order_by("-id")  # Para actualizar la lista después de eliminar
        return render(request, 'salesorder/salesorder-list.html', {'salesorders': salesorders})
    return HttpResponse(status=405)