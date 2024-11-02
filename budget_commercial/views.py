from collections import defaultdict
from django.shortcuts import get_object_or_404, render, redirect
from .forms import CommercialBudgetForm, CommercialBudgetItemFormSet
from .models import CommercialBudget

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
        print("Recibida solicitud POST en create_commercial_budget")
        form = CommercialBudgetForm(request.POST)
        if form.is_valid():
            # Save the parent instance first
            commercial_budget = form.save()
            # Now, create the formset with the saved instance
            formset = CommercialBudgetItemFormSet(request.POST, instance=commercial_budget)
            print(f"Formset válido: {formset.is_valid()}")
            if formset.is_valid():
                formset.save()  # Save the items
                print("Presupuesto comercial y detalles guardados exitosamente")
                return redirect('detail_commercial_budget', pk=commercial_budget.pk)
            else:
                print(f"Errores en el formset: {formset.errors}")
        else:
            print(f"Errores en el formulario: {form.errors}")
            formset = CommercialBudgetItemFormSet(request.POST)
        return render(request, 'commercial_budget/commercial_budget_form.html', {
            'form': form,
            'formset': formset,
        })
    else:
        print("Recibida solicitud GET en create_commercial_budget")
        form = CommercialBudgetForm()
        formset = CommercialBudgetItemFormSet()
    return render(request, 'commercial_budget/commercial_budget_form.html', {
        'form': form,
        'formset': formset,
    })


