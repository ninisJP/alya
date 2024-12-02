# views_budget.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Budget, BudgetItem
from .forms import AddBudgetItemPlus

def detail_budget_plus(request, pk):
    budget = get_object_or_404(Budget, pk=pk)
    form = AddBudgetItemPlus()
    items= budget.items.all()

    return render(request, 'budgetplus/budget_plus.html', {
        'budget': budget,
        'items': items,
        'form': form  
    })

def budget_item_plus(request, pk):
    budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        form = AddBudgetItemPlus(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.budget = budget
            new_item.save()

            return render(request, 'budgetplus/budget_item_plus.html', {
                'items': budget.items.all(), 
                'budget': budget
            })
    else:
        return redirect('detail_budget_plus', pk=pk)

def budget_item_delete(request, item_id):
    item = get_object_or_404(BudgetItem, id=item_id)
    budget = item.budget  
    item.delete()  

    items = budget.items.all()

    return render(request, 'budgetplus/budget_item_plus.html', {
        'items': items,
        'budget': budget,
    })
