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

class RequirementOrderDetailView(DetailView):
    model = RequirementOrder
    template_name = 'requirement_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context

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
