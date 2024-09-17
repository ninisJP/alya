from django.shortcuts import render, redirect, get_object_or_404
from .forms import BudgetForm, BudgetItemFormSet
from .models import Budget, BudgetItem
from django.db import models
from django.db.models import Sum



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
                    item.final_price = item.quantity * item.item.price
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
