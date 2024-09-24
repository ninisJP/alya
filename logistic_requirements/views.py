from django.shortcuts import render, redirect, get_object_or_404
from .forms import RequirementOrderForm, RequirementOrderItemFormSet
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView 
from .models import RequirementOrder

# Vista para listar todas las RequirementOrders
class RequirementOrderListView(ListView):
    model = RequirementOrder
    template_name = 'requirement_order_list.html'
    context_object_name = 'requirement_orders'

def create_requirement_order(request):
    if request.method == "POST":
        order_form = RequirementOrderForm(request.POST)
        formset = RequirementOrderItemFormSet(request.POST)

        if order_form.is_valid() and formset.is_valid():
            requirement_order = order_form.save()  # Guardar la orden primero

            items = formset.save(commit=False)
            for item in items:
                item.requirement_order = requirement_order  # Asignar la orden a los ítems
                item.save()

            return redirect('requirement_order_list')
    else:
        order_form = RequirementOrderForm()
        formset = RequirementOrderItemFormSet()

    return render(request, 'create_requirement_order.html', {
        'order_form': order_form,
        'formset': formset
    })



def edit_requirement_order(request, pk):
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)

    if request.method == "POST":
        order_form = RequirementOrderForm(request.POST, instance=requirement_order)
        formset = RequirementOrderItemFormSet(request.POST, instance=requirement_order)

        if order_form.is_valid() and formset.is_valid():
            order_form.save()

            items = formset.save(commit=False)
            for item in items:
                item.save()

            # El total_order se calculará automáticamente en el modelo
            return redirect('requirement_order_list')
        else:
            print(order_form.errors)
            print(formset.errors)
    else:
        order_form = RequirementOrderForm(instance=requirement_order)
        formset = RequirementOrderItemFormSet(instance=requirement_order)

    return render(request, 'requirements/edit_requirement_order.html', {
        'order_form': order_form,
        'formset': formset,
        'requirement_order': requirement_order
    })



