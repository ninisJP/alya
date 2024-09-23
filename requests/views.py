from django.shortcuts import render, redirect, get_object_or_404
from accounting_order_sales.models import SalesOrder, SalesOrderItem
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from .forms import CreateRequirementOrderForm, CreateRequirementOrderItemFormSet 
from django.views.generic import DetailView



def index_requests(request):
    sales_orders = SalesOrder.objects.all()
    return render(request, 'index_requests.html', {'sales_orders': sales_orders})

def my_requests(request):
    my_orders = RequirementOrder.objects.filter(user=request.user)
    return render(request, 'requests/my_requests.html', {'my_orders': my_orders})

def create_requests(request, order_id):
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    
    # Traer los ítems de SalesOrder como referencia, sin afectar el formset
    referencia_ordenventa = SalesOrderItem.objects.filter(salesorder=sales_order)

    if request.method == "POST":
        order_form = CreateRequirementOrderForm(request.POST)
        formset = CreateRequirementOrderItemFormSet(request.POST)

        if order_form.is_valid() and formset.is_valid():
            requirement_order = order_form.save(commit=False)
            requirement_order.sales_order = sales_order
            requirement_order.user = request.user  # Asignar el usuario actual al requerimiento
            requirement_order.save()

            items = formset.save(commit=False)
            for item in items:
                item.requirement_order = requirement_order
                item.save()

            return redirect('index_requests')
    else:
        order_form = CreateRequirementOrderForm(initial={'sales_order': sales_order})
        
        # Aquí sobreescribimos el formset para pasar la orden de venta al formulario de ítem
        formset = CreateRequirementOrderItemFormSet(
            queryset=RequirementOrderItem.objects.none(),  # No mostrar ítems previos
            form_kwargs={'sales_order': sales_order}  # Pasamos la orden de venta al formset
        )

    # Enviar los ítems como referencia visual sin afectar la lógica de creación
    return render(request, 'requests/create_requests.html', {
        'order_form': order_form,
        'formset': formset,
        'sales_order': sales_order,
        'referencia_ordenventa': referencia_ordenventa 
    })


class MyRequestDetail(DetailView):
    model = RequirementOrder
    template_name = 'requests/my_request_detail.html'
    context_object_name = 'order'




