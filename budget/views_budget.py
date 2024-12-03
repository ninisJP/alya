# views_budget.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Budget, BudgetItem, CatalogItem
from .forms import AddBudgetItemPlus
from decimal import Decimal
from decimal import ROUND_HALF_UP
from django.db import transaction

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

            if 'HORAS' in new_item.unit.upper():
                new_item.custom_price_per_day = (new_item.custom_price / new_item.item.life_time).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                new_item.custom_price_per_hour = (new_item.custom_price_per_day / 8).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                new_item.custom_quantity = Decimal(budget.budget_days) * 8 * new_item.quantity
                new_item.total_price = (new_item.custom_price_per_day * Decimal(budget.budget_days) * new_item.quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                new_item.custom_price_per_day = 0 
                new_item.total_price = new_item.quantity * new_item.custom_price

            new_item.save()
            budget.calculate_budget_price()

            return render(request, 'budgetplus/budget_item_plus.html', {
                'items': budget.items.all(),
                'budget': budget
            })
    else:
        return redirect('detail_budget_plus', pk=pk)

def budget_item_update(request, pk):
    budget = get_object_or_404(Budget, pk=pk)  # Obtener el presupuesto
    success_message = None

    if request.method == 'POST':
        try:
            with transaction.atomic():  # Asegurar que todos los cambios sean atómicos
                for item in budget.items.all():  # Iterar sobre cada ítem del presupuesto
                    # Obtener los datos modificados para cada ítem
                    quantity = request.POST.get(f'quantity_{item.id}')
                    custom_quantity = request.POST.get(f'custom_quantity_{item.id}')
                    custom_price_per_hour = request.POST.get(f'custom_price_per_hour_{item.id}')
                    custom_price_per_day = request.POST.get(f'custom_price_per_day_{item.id}')
                    custom_price = request.POST.get(f'custom_price_{item.id}')

                    # Verificar si los valores fueron modificados y actualizar
                    if quantity:
                        item.quantity = Decimal(quantity)
                    if custom_quantity:
                        item.custom_quantity = Decimal(custom_quantity)
                    if custom_price_per_hour:
                        item.custom_price_per_hour = Decimal(custom_price_per_hour)
                    if custom_price_per_day:
                        item.custom_price_per_day = Decimal(custom_price_per_day)
                    if custom_price:
                        item.custom_price = Decimal(custom_price)

                    # Recalcular el precio total del ítem
                    if 'HORAS' in item.unit.upper():
                        item.total_price = (item.custom_price_per_day * Decimal(budget.budget_days) * item.quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    else:
                        item.total_price = item.quantity * item.custom_price

                    item.save()  # Guardar el ítem actualizado en la base de datos

                # Recalcular el presupuesto total después de actualizar los ítems
                budget.calculate_budget_price()

                success_message = "Los cambios se guardaron correctamente."  # Mensaje de éxito

        except Exception as e:
            success_message = f"Hubo un error al guardar los cambios: {e}"  # Mensaje de error

        # Renderizar la página con los datos actualizados
        return render(request, 'budgetplus/budget_item_plus.html', {
            'items': budget.items.all(),
            'budget': budget,
            'success_message': success_message,
        })
    else:
        # Si no es una solicitud POST, redirigir al detalle del presupuesto
        return redirect('detail_budget_plus', pk=pk)


def budget_item_delete(request, item_id):
    item = get_object_or_404(BudgetItem, id=item_id)
    budget = item.budget  
    item.delete()

    budget.calculate_budget_price()

    items = budget.items.all()

    return render(request, 'budgetplus/budget_item_plus.html', {
        'items': items,
        'budget': budget,
    })

