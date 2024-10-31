from django.shortcuts import render

from alya.utils import search_model

from .forms import SearchPurchaseItemForm, NewItemForm
from .utils import get_all_purchase, get_all_items, new_item

def input_index(request):
	context = {}
	purchases = get_all_purchase()
	context['purchases'] = purchases
	return render(request, 'inputnewitem/home.html', context)

def input_new(request, purchase_pk):
	context = {}
	context_items, items = get_all_items(purchase_pk)
	context.update(context_items)
	context['search'] = SearchPurchaseItemForm()
	return render(request, 'inputnewitem/guide/home.html', context)

def input_new_search(request, purchase_pk):
	context = {}
	context_items, items = get_all_items(purchase_pk)
	context.update(context_items)

	if request.method == 'POST':
		form = SearchPurchaseItemForm(request.POST)
		# If search camp is void
		if form.is_valid() and (form.cleaned_data['sap_code']!="") :
			# Get search list
			status, purchase_items = search_model(items, 'sap_code', form.cleaned_data['sap_code'], accept_all=True)
			if purchase_items != {} :
				purchase_items = purchase_items.order_by('sap_code')
			if len(purchase_items)==1 :
				status = "yes"

			context['purchase_items'] = purchase_items
			context['search_status'] = status
			if status == "yes" :
				context['newitem'] = NewItemForm()

	context['search'] = SearchPurchaseItemForm()
	return render(request, 'inputnewitem/guide/list.html', context)

def input_new_item(request, purchase_item_pk):
	context = {}
	if request.method == 'POST':
		form = NewItemForm(request.POST)
		# If search camp is void
		if form.is_valid() :
			status = new_item(purchase_item_pk, form.cleaned_data['quantity'])
			context['newitem_status'] = status

	context['search'] = SearchPurchaseItemForm()
	return render(request, 'input/guide/list.html', context)
