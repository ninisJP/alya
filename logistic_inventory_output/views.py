from django.shortcuts import render, get_object_or_404

from accounting_order_sales.models import SalesOrder

from .forms import InventoryOutputForm, SearchSalesOrderForm
from .models import InventoryOutput, InventoryOutputItem
from .utils import check_items, search_salesorder

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

def output_new_list(request, salesorder_id):
    saleorder = get_object_or_404(SalesOrder, id=salesorder_id)
    output = InventoryOutput.objects.filter(sales_order=saleorder);
    context = {}
    if not output :
        output = InventoryOutput(sales_order=saleorder)
        output.save();
    return render(request, 'output/guide/home.html', context)

def output_see(request, output_id):
    outputs = get_object_or_404(InventoryOutput, id=output_id)
    items = InventoryOutputItem.objects.filter(output=output)
    context = {}
    context['outputs'] = outputs
    context['items'] = items
    return render(request, 'output/see.html', context)
