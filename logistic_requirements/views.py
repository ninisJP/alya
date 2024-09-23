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

            requirement_order = order_form.save()

            items = formset.save(commit=False)
            for item in items:
                item.requirement_order = requirement_order
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
    # Obtener la orden de requerimiento existente usando pk
    requirement_order = get_object_or_404(RequirementOrder, pk=pk)

    if request.method == "POST":
        # Actualizar el formulario con los datos existentes y los cambios enviados
        order_form = RequirementOrderForm(request.POST, instance=requirement_order)
        formset = RequirementOrderItemFormSet(request.POST, instance=requirement_order)

        if order_form.is_valid() and formset.is_valid():
            # Guardar los cambios en la orden y sus ítems
            order_form.save()
            formset.save()  # Guardar solo los cambios sin añadir ni eliminar ítems

            return redirect('requirement_order_list')  # Redirige a la vista que desees después de la edición
        else:
            # Mostrar los errores para debug
            print(order_form.errors)
            print(formset.errors)
    else:
        # Cargar el formulario y formset con los datos existentes
        order_form = RequirementOrderForm(instance=requirement_order)
        formset = RequirementOrderItemFormSet(request.POST or None, instance=requirement_order)


    return render(request, 'requirements/edit_requirement_order.html', {
        'order_form': order_form,
        'formset': formset,
        'requirement_order': requirement_order
    })

