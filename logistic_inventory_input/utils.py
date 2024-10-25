from django.shortcuts import get_object_or_404

import re

from logistic_inventory.models import Item
from logistic_inventory_output.models import InventoryOutput, InventoryOutputItem

from .models import InventoryInput

def search_items(form, list_items):
	# Get missing inventory items
	list_items = list(list_items.values('item'))

	regex_str = str(form.cleaned_data['sap_code'])

	status = "no"
	# If void
	if regex_str == "" :
		return status, list_items

	match_items = []
	for item in list_items :
		item_sap = Item.objects.get(item=item['item']).item.sap
		match = re.findall(regex_str, str(item_sap), re.IGNORECASE)
		match = ''.join(match)
		if len(match) :
			match_items.append(item)

	# Get model id
	list_id = []
	for item in match_items :
		id_name =list(item.keys())[0]
		list_id.append(item[id_name])

	# Get model
	model_list = InventoryOutputItem.objects.filter(pk__in=list_id)

	if len(model_list)==1 :
		status = "yes"

	return status, model_list

def get_all_items(output_pk):
	output = get_object_or_404(InventoryOutput, pk=output_pk)
	items = InventoryOutputItem.objects.filter(output=output.pk, returned=False)
	output_items_returned = InventoryOutputItem.objects.filter(output=output.pk, returned=True)

	items_returned = []
	for item in output_items_returned :
		items_returned.append(InventoryInput.objects.get(output_item=item))

	context = {}
	context['output'] = output
	context['output_items'] = items
	context['output_items_returned'] = items_returned
	return context, items

def new_item(outputitem_pk, quantity):
	status = "no"
	output_item = get_object_or_404(InventoryOutputItem, pk=outputitem_pk)

	# Quantity valid
	if output_item.quantity < quantity:
		return status

	# Get Inventory Item
	inventory_item = output_item.item

	# Create Input
	input_item = InventoryInput(
			output_item = output_item,
			quantity = quantity
			)
	input_item.save();

	inventory_item.quantity = inventory_item.quantity + quantity
	inventory_item.save()
	output_item.returned = True
	output_item.date_returned = input_item.date_create
	output_item.save()

	status = "yes"

	return status
