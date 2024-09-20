from django.shortcuts import render, redirect
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

# Vista para ver los detalles de una orden de requerimiento
class RequirementOrderDetailView(DetailView):
    model = RequirementOrder
    template_name = 'requirement_order_detail.html'
    context_object_name = 'order'

    # En caso quieras pasar los ítems de la orden a la plantilla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()  # Obtener los ítems de la orden de requerimiento
        return context

def create_requirement_order(request):
    if request.method == "POST":
        # Inicializamos el formulario principal y el formset con los datos POST
        order_form = RequirementOrderForm(request.POST)
        formset = RequirementOrderItemFormSet(request.POST)

        if order_form.is_valid() and formset.is_valid():
            # Guardamos la Orden de Requerimiento
            requirement_order = order_form.save()

            # Asignamos la orden de requerimiento a cada ítem y guardamos el formset
            items = formset.save(commit=False)
            for item in items:
                item.requirement_order = requirement_order
                item.save()
            return redirect('requirement_order_list')  # Redirige después de crear la orden
    else:
        # Inicializa los formularios vacíos
        order_form = RequirementOrderForm()
        formset = RequirementOrderItemFormSet()

    return render(request, 'create_requirement_order.html', {
        'order_form': order_form,
        'formset': formset
    })
