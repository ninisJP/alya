from django.shortcuts import render
from .models import Suppliers
from .forms import SuppliersForm
from django.shortcuts import render,get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponse, JsonResponse

# Create your views here.
# Iniciamos vista y metodos HTMX para tareas
def index_suppliers(request):
    suppliers = Suppliers.objects.all()
    context = {'form': SuppliersForm(), 'suppliers': suppliers}
    return render(request, 'suppliers/suppliers.html', context)

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
