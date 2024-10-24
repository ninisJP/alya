from django.shortcuts import get_object_or_404

from logistic_inventory_output.models import InventoryOutput, InventoryOutputItem

def search_items(form, list_items):
	# Get missing inventory items
	items = []
	print(list_items.values('items'))
#	for item in list_items :
#		item_exist = output_items.filter(item_requirement=item)
#		if not item_exist :
#			item_missing.append(item)
	print(items)


def get_all_items(output_pk):
	output = get_object_or_404(InventoryOutput, pk=output_pk)
	items = InventoryOutputItem.objects.filter(output=output.pk, returned=False)

	context = {}
	context['output'] = output
	context['output_items'] = items
	return context, items
