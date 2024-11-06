from django.shortcuts import get_object_or_404

from datetime import datetime

from logistic_inventory_input.models import InventoryInput
from logistic_inventory_output.models import InventoryOutputItem
from logistic_inventory_inputnewitem.models import InventoryInputNewItem
from alya import utils


def search_guide(form):

	context = {}
	model_list_input_returned = InventoryInput.objects.all()
	model_list_input_purchase = InventoryInputNewItem.objects.all()
	model_list_output = InventoryOutputItem.objects.all()

	date_start = form.cleaned_data['date_start']
	date_end = form.cleaned_data['date_end']

	if not date_end :
		date_end = datetime.today().date()

	if date_start :
		# Check valid date
		if date_end < date_start :
			return context
		model_list_input_returned = model_list_input_returned.filter(date_create__range=[date_start, date_end])
		model_list_input_purchase = model_list_input_purchase.filter(date_create__range=[date_start, date_end])
		model_list_output = model_list_output.filter(date_create__range=[date_start, date_end])

	print(model_list_input_returned)
	print(model_list_input_purchase)
	print(model_list_output)

	context['outputsr'] = model_list_output
	context['inputs_returned'] = model_list_input_returned
	context['inputs_purchase'] = model_list_input_purchase

	return context
