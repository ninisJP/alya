from django.shortcuts import render
from .models import Suppliers
from .forms import SuppliersForm
from django.shortcuts import render,get_object_or_404
from django.views.decorators.http import require_POST, require_http_methods
from django.http import HttpResponse, JsonResponse

# Create your views here.
# Iniciamos vista y metodos HTMX para tareas
def suppliers(request):
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
            user_tasks = Suppliers.objects.all()
            context = {'suppliers': supplier}
            return render(request, 'suppliers/suppliers-list.html', context)
    else:
        form = SuppliersForm()

    return render(request, 'suppliers/suppliers-form.html', {'form': form})

def edit_suppliers(request, supplier_id):
    task = get_object_or_404(Suppliers, id=supplier_id)
    if request.method == 'GET':
        form = SuppliersForm(instance=suppliers)
        return render(request, 'suppliers/edit-suppliers-form.html', {'form': form, 'task': task})
    elif request.method == 'POST':
        form = SuppliersForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            suppliers = Suppliers.objects.all()
            return render(request, 'suppliers/suppliers-list.html', {'tasks': suppliers})
    return HttpResponse(status=405)

def delete_suppliers(request, supplier_id):
    suppliers = get_object_or_404(Suppliers, id=supplier_id)
    if request.method == 'DELETE':
        suppliers.delete()
        return render(request, 'suppliers/suppliers-list.html')
    return HttpResponse(status=405)
