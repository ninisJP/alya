from django.shortcuts import render, get_object_or_404

from logistic_inventory_output.models import InventoryOutput, InventoryOutputItem

from .forms import SearchOutputItemForm, RetornedOutputItemForm
from .utils import get_all_items, search_items, new_item, get_all_outputs

def input_index(request):
	context = {}
	#context['outputs'] = InventoryOutput.objects.filter(returned=False)
	outputs = get_all_outputs()
	context['outputs'] = outputs
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
			status, output_items = search_items(form, items)
			context['output_items'] = output_items
			context['search_status'] = status
			if status == "yes" :
				context['newitem'] = RetornedOutputItemForm()

	context['search'] = SearchOutputItemForm()
	return render(request, 'input/guide/list.html', context)

def input_new_item(request, outputitem_pk):
	context = {}
	if request.method == 'POST':
		form = RetornedOutputItemForm(request.POST)
		# If search camp is void
		if form.is_valid() :
			status = new_item(outputitem_pk, form.cleaned_data['quantity'])
			context['newitem_status'] = status

	context['search'] = SearchOutputItemForm()
	return render(request, 'input/guide/list.html', context)
