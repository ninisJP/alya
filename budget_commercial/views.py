from collections import defaultdict
from django.shortcuts import get_object_or_404, render, redirect
from .forms import CommercialBudgetForm, CommercialBudgetItemFormSet
from .models import CommercialBudget
from django.contrib import messages


def index_budget_commercial(request):
    """Renderiza la pagina principal del budget_commercial"""
    budgets = CommercialBudget.objects.all()
    return render(request, 'index_budget_commercial.html', {'budgets': budgets})

def detail_commercial_budget(request, pk):
    budget = get_object_or_404(CommercialBudget, pk=pk)
    items_by_category = defaultdict(list)

    # Imprimir todos los ítems relacionados con el presupuesto en la consola
    all_items = budget.commercial_items.all()
    print("Lista de ítems asociados al presupuesto:")
    for item in all_items:
        print(f"Descripción: {item.item.description}, Categoría: {item.item.category}, Cantidad: {item.quantity}, Precio Total: {item.total_price}")
        items_by_category[item.item.category].append(item)

    return render(request, 'commercial_budget/detail_commercial_budget.html', {
        'budget': budget,
        'items_by_category': dict(items_by_category),
    })

def create_commercial_budget(request):
    if request.method == 'POST':
        print("POST data:", request.POST)  # Imprime todo el contenido de request.POST para verificar que los datos llegan correctamente

        form = CommercialBudgetForm(request.POST)
        formset = CommercialBudgetItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            result = form.is_valid() and formset.is_valid()
            print(result)
            commercial_budget = form.save()  
            formset.instance = commercial_budget 
            formset.save()  
            print("Presupuesto comercial y sus ítems guardados exitosamente.")
            return redirect('detail_commercial_budget', pk=commercial_budget.pk)
        else:
            print("Errores en el formulario:", form.errors)
            print("Errores en el formset:", formset.errors)  

    else:
        form = CommercialBudgetForm()
        formset = CommercialBudgetItemFormSet()

    return render(request, 'commercial_budget/commercial_budget_form.html', {
        'form': form,
        'formset': formset,
    })
    
def delete_commercial_budget(request, pk):
    budget = get_object_or_404(CommercialBudget, pk=pk)

    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'El presupuesto ha sido eliminado exitosamente.')
        return redirect('index_budget_commercial')  # Redirigir a la lista de presupuestos

    return render(request, 'commercial_budget/delete_commercial_budget.html', {'budget': budget})

