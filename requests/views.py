from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from accounting_order_sales.models import SalesOrder, SalesOrderItem
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from .forms import CreateRequirementOrderForm, CreateRequirementOrderItemFormSet 
from django.views.generic import DetailView
from django.forms import inlineformset_factory
from .forms import CreateRequirementOrderForm, CreateRequirementOrderItemForm, CreateRequirementOrderItemFormSet
from django.contrib import messages
from django.core.exceptions import ValidationError

def index_requests(request):
    sales_orders = SalesOrder.objects.all().order_by('-id')
    return render(request, 'index_requests.html', {'sales_orders': sales_orders})

def my_requests(request):
    my_orders = RequirementOrder.objects.filter(user=request.user).order_by('-id')
    return render(request, 'requests/my_requests.html', {'my_orders': my_orders})

def delete_order(request, order_id):
    if request.method == 'DELETE':
        order = get_object_or_404(RequirementOrder, id=order_id, user=request.user)
        order.delete()
        # Aquí devolvemos un fragmento HTML directamente
        return HttpResponse('<div class="alert alert-success">¡El pedido ha sido eliminado correctamente!</div>', content_type='text/html')
    return HttpResponse('<div class="alert alert-danger">Hubo un problema al eliminar el pedido.</div>', status=400)

def create_requests(request, order_id):
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    referencia_ordenventa = SalesOrderItem.objects.filter(salesorder=sales_order)

    if request.method == "POST":
        order_form = CreateRequirementOrderForm(request.POST)
        formset = CreateRequirementOrderItemFormSet(request.POST, request.FILES, form_kwargs={'sales_order': sales_order})

        if order_form.is_valid() and formset.is_valid():
            try:
                requirement_order = order_form.save(commit=False)
                requirement_order.sales_order = sales_order
                requirement_order.user = request.user
                requirement_order.save()

                items = formset.save(commit=False)
                for item in items:
                    item.requirement_order = requirement_order
                    item.price = item.price or item.sales_order_item.price
                    
                    try:
                        item.clean()
                        item.save()
                    except ValidationError as e:
                        item_name = item.sales_order_item.description
                        for message in e.messages:
                            messages.error(request, f"Error en el ítem '{item_name}': {message}")

                messages.success(request, "Pedido creado exitosamente.")
                return redirect('index_requests')

            except ValidationError as e:
                messages.error(request, str(e))
        else:
            for form in formset:
                if form.errors:
                    item_name = form.cleaned_data.get('sales_order_item', 'Sin nombre')
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f"Error en {item_name}: {field} - {error}")
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        order_form = CreateRequirementOrderForm(initial={'sales_order': sales_order})
        formset = CreateRequirementOrderItemFormSet(
            queryset=RequirementOrderItem.objects.none(),
            form_kwargs={'sales_order': sales_order}
        )

    return render(request, 'requests/create_requests.html', {
        'order_form': order_form,
        'formset': formset,
        'sales_order': sales_order,
        'referencia_ordenventa': referencia_ordenventa
    })

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import CreateRequirementOrderForm, PrepopulatedRequirementOrderItemForm

def create_prepopulated_request(request, order_id):
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    sales_order_items = SalesOrderItem.objects.filter(salesorder=sales_order)

    # Prepare initial data
    initial_items = [
        {
            'sales_order_item': item.id,
            'quantity_requested': item.amount,
        }
        for item in sales_order_items
    ]

    PrepopulatedFormSet = inlineformset_factory(
        RequirementOrder,
        RequirementOrderItem,
        form=PrepopulatedRequirementOrderItemForm,
        extra=len(initial_items),
        can_delete=True  # Allow users to delete items
    )

    if request.method == "POST":
        order_form = CreateRequirementOrderForm(request.POST)
        formset = PrepopulatedFormSet(
            request.POST,
            form_kwargs={'sales_order': sales_order}
        )

        if order_form.is_valid() and formset.is_valid():
            try:
                requirement_order = order_form.save(commit=False)
                requirement_order.sales_order = sales_order
                requirement_order.user = request.user
                requirement_order.save()

                items = formset.save(commit=False)
                for item in items:
                    item.requirement_order = requirement_order
                    item.save()

                messages.success(request, "Pedido creado exitosamente.")
                return redirect('index_requests')

            except ValidationError as e:
                messages.error(request, str(e))
        else:
            # Display errors for debugging
            print("Order form errors:", order_form.errors)
            print("Formset errors:", formset.errors)
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        order_form = CreateRequirementOrderForm(initial={'sales_order': sales_order})
        formset = PrepopulatedFormSet(
            queryset=RequirementOrderItem.objects.none(),
            initial=initial_items,
            form_kwargs={'sales_order': sales_order}
        )

    # Attach item descriptions to each form
    for form, item in zip(formset.forms, sales_order_items):
        form.item_description = item.description

    return render(request, 'requests/create_prepopulated_request.html', {
        'order_form': order_form,
        'formset': formset,
        'sales_order': sales_order,
    })


class MyRequestDetail(DetailView):
    model = RequirementOrder
    template_name = 'requests/my_request_detail.html'
    context_object_name = 'order'   