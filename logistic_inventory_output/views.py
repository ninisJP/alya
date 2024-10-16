from django.shortcuts import render, get_object_or_404

from .forms import InventoryOutputForm
from .models import InventoryOutput, InventoryOutputItem
from .utils import check_items

# Create your views here.

def output_list(request):
    outputs = InventoryOutput.objects.all()
    context = {'outputs': outputs}
    return render(request, 'output/list.html', context)

def output_new(request):
    context = {}
    if request.method == 'POST':
        form = InventoryOutputForm(request.POST)
        status = "no"
        if form.is_valid():
            status = "item_error"
            item_no_found = check_items(form.data['sales_order'])
            if len(item_no_found) == 0 :
                form.save()
                status = "yes"
            else :
                context['item_no_found'] = item_no_found
        context['status'] = status

    context['form'] = InventoryOutputForm()

    return render(request, 'output/form.html', context)

def output_see(request, output_id):
    output = get_object_or_404(InventoryOutput, id=output_id)
    items = InventoryOutputItem.objects.filter(output=output)
    context = {}
    context['output'] = output
    context['items'] = items
    return render(request, 'output/see.html', context)
