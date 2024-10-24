from django.shortcuts import render, get_object_or_404

from logistic_inventory_output.models import InventoryOutput, InventoryOutputItem

from .forms import SearchOutputItemForm
from .utils import get_all_items, search_items

def input_index(request):
	context = {}
	context['outputs'] = InventoryOutput.objects.filter(returned=False)
	return render(request, 'input/home.html', context)

def input_new(request, output_pk):
	context = {}
	context_items, items = get_all_items(output_pk)
	context.update(context_items)
	context['search'] = SearchOutputItemForm()
	return render(request, 'input/guide/home.html', context)

def input_new_search(request, output_pk):
	context = {}
	context_items, items = get_all_items(output_pk)
	context.update(context_items)

	if request.method == 'POST':
		form = SearchOutputItemForm(request.POST)
		# If search camp is void
		if form.is_valid() and (form.cleaned_data['sap_code']!="") :
			# Get search list
			#status, saleorder_items, inventory_items = search_saleorder_item(form, item_missing)
			print("ok")
			search_items(form, items)
			#context['saleorder_items'] = saleorder_items
			#context['inventory_items'] = inventory_items
			#context['valid_item'] = status
			#context['search_active'] = "yes"

	context['search'] = SearchOutputItemForm()
	return render(request, 'input/guide/list.html', context)
