from django.shortcuts import render, get_object_or_404

from accounting_order_sales.models import SalesOrder, SalesOrderItem
from alya import utils
from logistic_inventory.models import Item
from logistic_requirements.models import RequirementOrder, RequirementOrderItem

from .forms import InventoryOutputForm, SearchSalesOrderForm, SearchSalesOrderItemForm
from .models import InventoryOutput, InventoryOutputItem
from .utils import check_items, search_salesorder, search_saleorder_item, get_all_items, get_all_outputs


def output_index(request):
    outputs = get_all_outputs()
    context = {'outputs': outputs}
    return render(request, 'output/home.html', context)

def output_new_salesorder(request):
    context = {}
    context['salesorders'] = SalesOrder.objects.all()
    if request.method == 'POST':
        form = SearchSalesOrderForm(request.POST)
        if form.is_valid():
            status, salesorders = search_salesorder(SalesOrder.objects.all(), form)
            if salesorders != {} :
                salesorders = salesorders.order_by('sapcode')
            context['salesorders'] = salesorders
            context['search_status'] = status
            return render(request, 'output/guide/salesorder/list.html', context)

    context['search'] = SearchSalesOrderForm()
    return render(request, 'output/guide/salesorder/home.html', context)

def output_new(request, saleorder_id):
    saleorder = get_object_or_404(SalesOrder, id=saleorder_id)
    context = {}

    # Get output
    output = InventoryOutput.objects.filter(sale_order=saleorder);
    if not output :
        # Create output
        output = InventoryOutput(sale_order=saleorder)
        output.save()
    else:
        # Get one output
        output = output[0]

    context_items, item_missing = get_all_items(output.pk)
    context.update(context_items)

    context['search'] = SearchSalesOrderItemForm()

    return render(request, 'output/guide/home.html', context)

def output_new_list(request, output_pk):
    context = {}
    context_items, item_missing = get_all_items(output_pk)
    context.update(context_items)

    if request.method == 'POST':
        form = SearchSalesOrderItemForm(request.POST)
        # If search camp is void
        if form.is_valid() and (form.cleaned_data['sap_code']!="") :
            # Get search list
            status, requirements_items, inventory_items = search_saleorder_item(form, item_missing)
            context['requirements_items'] = requirements_items
            context['inventory_items'] = inventory_items
            context['valid_item'] = status
            context['search_active'] = "yes"

    context['search'] = SearchSalesOrderItemForm()
    return render(request, 'output/guide/list.html', context)

def output_new_item(request, output_pk, requirement_item_pk, logistic_item_pk):
    output = get_object_or_404(InventoryOutput, pk=output_pk)
    requirement_item = get_object_or_404(RequirementOrderItem, pk=requirement_item_pk)
    logistic_item = get_object_or_404(Item, pk=logistic_item_pk)

    context = {}
    # Valid quantity: never is major to available
    if logistic_item.quantity < requirement_item.quantity_requested :
        return render(request, 'output/guide/list.html', context)
    # Create Output Item
    output_item = InventoryOutputItem(
            item = logistic_item,
            item_requirement = requirement_item,
            output = output,
            quantity = requirement_item.quantity_requested
            )
    output_item.save()

    logistic_item.quantity = logistic_item.quantity - requirement_item.quantity_requested
    logistic_item.save()
    # Get quantity
    context = {}
    context_items, item_missing = get_all_items(output_pk)
    context.update(context_items)
    return render(request, 'output/guide/list.html', context)

def output_see(request, output_pk):
    context = {}
    context_items, item_missing = get_all_items(output_pk)
    context.update(context_items)

    context['search'] = SearchSalesOrderItemForm()

    return render(request, 'output/see.html', context)

def output_see_list(request, output_pk):
    context = {}
    context_items, item_missing = get_all_items(output_pk)
    context.update(context_items)

    if request.method == 'POST':
        form = SearchSalesOrderItemForm(request.POST)
        # If search camp is void
        if form.is_valid() and (form.cleaned_data['sap_code']!="") :
            # Get search list
            status, requirements_items, inventory_items = search_saleorder_item(form, item_missing)
            context['requirements_items'] = requirements_items

    context['search'] = SearchSalesOrderItemForm()
    return render(request, 'output/guide/list.html', context)
