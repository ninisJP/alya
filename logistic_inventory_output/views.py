from django.shortcuts import render, get_object_or_404

from accounting_order_sales.models import SalesOrder, SalesOrderItem
from alya import utils

from .forms import InventoryOutputForm, SearchSalesOrderForm, SearchSalesOrderItemForm
from .models import InventoryOutput, InventoryOutputItem
from .utils import check_items, search_salesorder, search_salesorder_item

# Create your views here.

def output_list(request):
    outputs = InventoryOutput.objects.all()
    context = {'outputs': outputs}
    return render(request, 'output/list.html', context)

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


    #if request.method == 'POST':
    #    form = SalesOrder(request.POST)
    #    status = "no"
    #    if form.is_valid():
    #        status = "item_error"
    #        items_no_found, items_no_enough = check_items(form.data['sales_order'])
    #        if (len(items_no_found)==0) and (len(items_no_enough)==0):
    #            form.save()
    #            status = "yes"
    #        else :
    #            context['items_no_found'] = items_no_found
    #            context['items_no_enough'] = items_no_enough
    #    context['status'] = status

    #context['form'] = InventoryOutputForm()

    #return render(request, 'output/guide/0_salesorder.html', context)

def output_new(request, saleorder_id):
    saleorder = get_object_or_404(SalesOrder, id=saleorder_id)
    context = {}

    # Get output
    output = InventoryOutput.objects.filter(sale_order=saleorder);
    if not output :
        # Create output
        output = InventoryOutput(sale_order=saleorder)
        output.save();
    else:
        # Get one output
        output = output[0]

    context['output'] = output
    context['output_items'] = InventoryOutputItem.objects.filter(output=output.pk)
    context['saleorder_items'] = SalesOrderItem.objects.filter(salesorder=output.sale_order)

    context['search'] = SearchSalesOrderItemForm()

    return render(request, 'output/guide/home.html', context)

def output_new_list(request, output_pk):
    output = get_object_or_404(InventoryOutput, pk=output_pk)
    context = {}
    context['output'] = output
    context['output_items'] = InventoryOutputItem.objects.filter(output=output.pk)
    context['saleorder_items'] = SalesOrderItem.objects.filter(salesorder=output.sale_order)

    if request.method == 'POST':
        form = SearchSalesOrderItemForm(request.POST)
        # If search camp is void
        if form.is_valid() and (form.cleaned_data['sap_code']!="") :
            # Get search list
            status, saleorder_items, inventory_items = search_salesorder_item(form)
            context['saleorder_items'] = saleorder_items
            context['inventory_items'] = inventory_items
            context['valid_item'] = status
            context['search_active'] = "yes"

    context['search'] = SearchSalesOrderItemForm()
    return render(request, 'output/guide/list.html', context)

def output_new_item(request, output_pk, saleorder_item_pk):
    return {}

def output_see(request, output_id):
    outputs = get_object_or_404(InventoryOutput, id=output_id)
    items = InventoryOutputItem.objects.filter(output=output)
    context = {}
    context['outputs'] = outputs
    context['items'] = items
    return render(request, 'output/see.html', context)
