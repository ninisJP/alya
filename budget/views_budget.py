# See LICENSE file for copyright and license details.
"""
Budget views (plus)
"""
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import Budget, BudgetItem
from .forms import AddBudgetItemPlus, BudgetEditNewForm, BudgetPlusForm


def create_budget_plus(request):
    """
    Create a budget
    """

    if request.method == 'POST':
        form = BudgetPlusForm(request.POST)
        if form.is_valid():
            budget = form.save()
            return redirect('detail_budget_plus', pk=budget.pk)
    return None


def detail_budget_plus(request, pk):
    """
    Show budget detail
    """

    budget = get_object_or_404(Budget, pk=pk)
    form = AddBudgetItemPlus()
    items = budget.items.all()
    context = {'budget': budget, 'items': items, 'form': form}

    return render(
        request,
        'budgetplus/budget_plus.html',
        context
    )


def only_detail_budget_plus(request, pk):
    """
    Show budget detail no edition
    """
    budget = get_object_or_404(Budget, pk=pk)
    items = budget.items.all()
    context = {'budget': budget, 'items': items}

    return render(
        request,
        'budgetplus/budget_only_detail_plus.html',
        context
    )


def update_budget_partial_plus(request, pk):
    """
    Update the budget
    """

    budget = get_object_or_404(Budget, pk=pk)
    form = BudgetEditNewForm(request.POST or None, instance=budget)

    if request.method == "POST" and form.is_valid():
        form.save()
        return render(
            request,
            "budgetplus/budget_detail_plus.html",
            {"budget": budget}
        )

    return render(
        request,
        "partials/_budget_form.html",
        {"form": form, "budget": budget}
    )


def budget_item_plus(request, pk):
    """
    Show budget items
    """

    budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        form = AddBudgetItemPlus(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.budget = budget

            # Item life item
            if new_item.item.life_time == 0 or new_item.item.life_time is None:
                new_item.item.life_time = 365

            # TODO: check default custom_price and
            #   alert from void camps in form
            if new_item.unit:
                if 'HORAS' in new_item.unit.upper():
                    new_item.custom_price_per_day = (
                        new_item.custom_price /
                        new_item.item.life_time
                    ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    new_item.custom_price_per_hour = (
                        new_item.custom_price_per_day / 8
                    ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    new_item.custom_quantity = (
                        Decimal(budget.budget_days) *
                        8 *
                        new_item.quantity
                    )
                    new_item.total_price = (
                        new_item.custom_price_per_day *
                        Decimal(budget.budget_days) *
                        new_item.quantity
                    ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                new_item.custom_price_per_day = 0
                new_item.total_price = (
                    new_item.quantity *
                    new_item.custom_price
                )

            new_item.save()
            budget.update_budget_price()

            return render(
                request,
                'budgetplus/budget_item_plus.html',
                {
                    'items': budget.items.all(),
                    'budget': budget
                }
            )
    else:
        return redirect('detail_budget_plus', pk=pk)


def budget_item_update(request, pk):
    """
    Update the budget items
    """

    budget = get_object_or_404(Budget, pk=pk)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                for item in budget.items.all():
                    quantity = request.POST.get(f'quantity_{item.id}')
                    custom_quantity = request.POST.get(
                        f'custom_quantity_{item.id}'
                    )
                    custom_price_per_hour = request.POST.get(
                        f'custom_price_per_hour_{item.id}'
                    )
                    custom_price_per_day = request.POST.get(
                        f'custom_price_per_day_{item.id}'
                    )
                    custom_price = request.POST.get(f'custom_price_{item.id}')
                    coin = request.POST.get(f'coin_{item.id}')
                    unit = request.POST.get(f'unit_{item.id}')

                    if quantity:
                        item.quantity = Decimal(quantity)
                    if custom_quantity:
                        item.custom_quantity = Decimal(custom_quantity)
                    if custom_price_per_hour:
                        item.custom_price_per_hour = Decimal(
                            custom_price_per_hour
                        )
                    if custom_price_per_day:
                        item.custom_price_per_day = Decimal(
                            custom_price_per_day
                        )
                    if custom_price:
                        item.custom_price = Decimal(custom_price)
                    if coin:
                        item.coin = coin
                    if unit:
                        item.unit = unit

                    if 'HORAS' in item.unit.upper():
                        item.total_price = (
                            item.custom_price_per_day *
                            Decimal(budget.budget_days) *
                            item.quantity
                        ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    else:
                        item.total_price = item.quantity * item.custom_price

                    item.save()

                budget.update_budget_price()

        except Exception:
            # TODO: remove pass
            pass

        return render(request, 'budgetplus/budget_item_plus.html', {
            'items': budget.items.all(),
            'budget': budget,
        })

    return redirect('detail_budget_plus', pk=pk)

def budget_item_delete(request, item_id):
    """Remove budget item"""
    with transaction.atomic():
        item = get_object_or_404(BudgetItem, id=item_id)
        budget = item.budget
        item.delete()
        budget.remove_single_item_price(item)
    items = budget.items.all()
    context = {'items': items, 'budget': budget}
    return render(request, 'budgetplus/budget_item_plus.html', context)
