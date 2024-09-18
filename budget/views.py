from django.contrib import messages
from django.db import models
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from .forms import BudgetForm, BudgetItemFormSet, CatalogItemForm, SearchCatalogItemForm
from .models import Budget, BudgetItem, CatalogItem


def index_budget(request):
    budgets = Budget.objects.all()  # Recupera todos los presupuestos
    return render(request, 'index_budget.html', {'budgets': budgets})

def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        formset = BudgetItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            budget = form.save()
            formset.instance = budget  # Vincula el formset al budget
            formset.save()  # Guardar el formset directamente, sin preocuparse por `final_price`
            return redirect('detail_budget', pk=budget.pk)
    else:
        form = BudgetForm()
        formset = BudgetItemFormSet()

    return render(request, 'budget/create_budget.html', {
        'form': form,
        'formset': formset,
    })

def edit_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        formset = BudgetItemFormSet(request.POST, instance=budget)

        if form.is_valid() and formset.is_valid():
            budget = form.save()
            items = formset.save(commit=False)
            for item in items:
                item.budget = budget
                if item.item and item.quantity:
                    item.final_price = item.quantity * item.item.unit_price
                item.save()

            for obj in formset.deleted_objects:
                obj.delete()

            # Calcular el precio final total
            total_final_price = budget.items.aggregate(total=Sum('final_price'))['total'] or 0
            budget.budget_final_price = total_final_price
            budget.save()

            return redirect('detail_budget', pk=budget.pk)
        else:
            # Imprimir errores en la consola para depuracións
            print("Formulario principal no válido:", form.errors)
            print("Formset no válido:", formset.errors)
    else:
        form = BudgetForm(instance=budget)
        formset = BudgetItemFormSet(instance=budget)

    return render(request, 'budget/edit_budget.html', {
        'form': form,
        'formset': formset,
        'budget': budget,
    })


def detail_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    budget_items = budget.items.all()  # Recupera todos los ítems asociados a este presupuesto
    return render(request, 'budget/detail_budget.html', {'budget': budget, 'budget_items': budget_items})

def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'El presupuesto ha sido eliminado exitosamente.')
        return redirect('index_budget')  # Redirigir a la lista de presupuestos

    return render(request, 'budget/delete_budget.html', {'budget': budget})

def duplicate_budget(request, pk):
    original_budget = get_object_or_404(Budget, pk=pk)
    
    # Copiar el presupuesto original sin guardar inmediatamente
    original_budget.pk = None  # Esto asegura que se asigne un nuevo ID
    original_budget.budget_name = f'Copia de {original_budget.budget_name}'
    original_budget.save()  # Ahora guardamos el presupuesto duplicado, se asigna un nuevo ID
    
    # Duplicar cada ítem asociado al presupuesto original
    for item in original_budget.items.all():
        item.pk = None  # Esto asegura que se asigne un nuevo ID al item duplicado
        item.budget = original_budget  # Reasignamos el nuevo budget
        item.save()
    
    return redirect('detail_budget', pk=original_budget.pk)











def catalog(request):
    user_tasks = Catalog.objects.all()
    context = {'form': TaskForm(), 'tasks': user_tasks}
    return render(request, '', context)

# CATALOG
def catalog(request):
    context = {'form': CatalogItemForm(), 'search': SearchCatalogItemForm()}
    return render(request, 'catalog/catalog.html', context)

def catalog_edit(request, catalog_id):
    catalog = get_object_or_404(Catalog, id=catalog_id)
    if request.method == 'GET':
        form = CatalogItemForm(instance=catalog)
        context = {
                'form': form,
                'catalog': catalog,
                }
        return render(request, 'catalog/catalog_edit.html', context)
    elif request.method == 'POST':
        form = CatalogItemForm(request.POST, instance=catalog)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
            context = {
                    'form': form,
                    'catalog': catalog,
                    }
        context['status'] = status
        return render(request, 'catalog/catalog_edit.html', context)
    return HttpResponse(status=405)

def catalog_new(request):
    context = {}
    if request.method == 'POST':
        form = CatalogItemForm(request.POST)
        status = "no"
        if form.is_valid():
            status = "yes"
            form.save()
        context['status'] = status

    context['form'] = CatalogItemForm()

    return render(request, 'catalog/catalog_form.html', context)

def catalog_search(request):
    context = {}
    if request.method == 'POST':
        form = SearchCatalogItemForm(request.POST)
        if form.is_valid():

            # Search catalogs
            #status, catalogs = search_catalog(CatalogItem.objects.all(), form)
            status, catalogs = utils.search_model(CatalogItem.objects.all(), 'name', form.cleaned_data['name'], accept_all=True)
            if catalogs != {} :
                catalogs = catalogs.order_by('name')

            # Sort
            #catalogs = sort_catalog(catalogs)

            context['catalogs'] = catalogs
            context['search_status'] = status
    context['search'] = SearchCatalogItemForm()
    return render(request, 'catalog/catalog_list.html', context)
