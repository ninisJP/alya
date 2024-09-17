from django.shortcuts import render, redirect, get_object_or_404
from .forms import BudgetForm, BudgetItemFormSet
from .models import Budget
 
def index_budget(request):
    budgets = Budget.objects.all()  # Recupera todos los presupuestos
    return render(request, 'index_budget.html', {'budgets': budgets})

def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        formset = BudgetItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            budget = form.save()
            items = formset.save(commit=False)
            for item in items:
                item.budget = budget
                # Asegúrate de que item.item y item.quantity están disponibles y son válidos
                if item.item and item.quantity:
                    item.final_price = item.quantity * item.item.unit_price
                item.save()
            formset.save_m2m()
            return redirect('detail_budget', pk=budget.pk)
    else:
        form = BudgetForm()
        formset = BudgetItemFormSet()

    return render(request, 'budget/create_budget.html', {
        'form': form,
        'formset': formset,
    })

def detail_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    budget_items = budget.items.all()  # Recupera todos los ítems asociados a este presupuesto
    return render(request, 'budget/detail_budget.html', {'budget': budget, 'budget_items': budget_items})
