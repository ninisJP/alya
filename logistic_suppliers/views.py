from django.shortcuts import render
from .models import Suppliers
from .forms import SuppliersForm
from accounting_order_sales.models import PurchaseOrderItem
from django.shortcuts import render,get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponse, JsonResponse
from django.db.models import Q

# Create your views here.
# Iniciamos vista y metodos HTMX para tareas
def index_suppliers(request):
    suppliers = Suppliers.objects.all()
    context = {'form': SuppliersForm(), 'suppliers': suppliers}
    return render(request, 'suppliers/suppliers.html', context)


# Add Search Supplier
def supplier_search(request):
    query = request.GET.get('q','')
    if query:
        suppliers=Suppliers.objects.filter(Q(document__icontains=query) | Q(name__icontains=query) | Q(bank__icontains=query)| Q(currency__icontains=query)).order_by('-id')
    else:
        suppliers=Suppliers.objects.all().order_by('-id') 
    
    context={'suppliers':suppliers , 'form': SuppliersForm()}
    return render(request,'suppliers/suppliers_list.html', context)

def create_suppliers(request):
    if request.method == 'POST':
        form = SuppliersForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.user = request.user
            supplier.save()
            suppliers = Suppliers.objects.all()
            context = {'suppliers': suppliers}
            return render(request, 'suppliers/suppliers_list.html', context)
    else:
        form = SuppliersForm()

    return render(request, 'suppliers/suppliers_form.html', {'form': form})


def edit_suppliers(request, supplier_id):
    supplier = get_object_or_404(Suppliers, id=supplier_id)
    
    if request.method == 'GET':
        form = SuppliersForm(instance=supplier)
        return render(request, 'suppliers/suppliers_edit.html', {'form': form, 'supplier': supplier})
    
    elif request.method == 'POST':
        form = SuppliersForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            suppliers = Suppliers.objects.all()
            return render(request, 'suppliers/suppliers_list.html', {'suppliers': suppliers})
    
    return HttpResponse(status=405)


def delete_suppliers(request, supplier_id):
    suppliers = get_object_or_404(Suppliers, id=supplier_id)  
    if request.method == 'POST':  
        suppliers.delete()  
        return render(request, 'suppliers/suppliers_list.html')  
    return HttpResponse(status=405) 

def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(Suppliers, id=supplier_id)
    # Obtener todas las órdenes de compra asociadas a este proveedor
    purchase_orders = PurchaseOrderItem.objects.filter(supplier=supplier)

    context = {
        'supplier': supplier,
        'purchase_orders': purchase_orders
    }

    return render(request, 'suppliers/supplier_detail.html', context)
