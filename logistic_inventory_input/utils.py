from django.shortcuts import get_object_or_404

from logistic_inventory_output.models import InventoryOutput, InventoryOutputItem


def get_inputs():
	outputs_items = list(InventoryOutputItem.objects.all().values('output'))

	# Get all output
	outputs = []
	for item in outputs_items :
		outputs.append(item['output'])

	outputs = set(outputs)

	outputs = InventoryOutput.objects.filter(pk__in=outputs)
	return outputs
