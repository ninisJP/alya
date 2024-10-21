from django.shortcuts import get_object_or_404

from .models import InventoryOutput, InventoryOutputItem

from accounting_order_sales.models import SalesOrder, SalesOrderItem
from alya import utils
from logistic_inventory.models import Item


def check_items(order_id):

	order = SalesOrder.objects.get(pk=order_id)
	all_items = SalesOrderItem.objects.filter(salesorder=order_id)

	item_no_exist = []
	item_no_enough = []
	for item in all_items :
		inventory_item = Item.objects.filter(item_id=item.sap_code)
		if not inventory_item :
			new_no_item = {'sap_code': item.sap_code,
					'description': item.description
				}
			item_no_exist.append(new_no_item)
			continue
		if item.amount <= inventory_item[0].quantity :
			continue
		new_no_item = {'sap_code': inventory_item[0].item_id,
				'description': inventory_item[0].description,
				'quantity_necesary': item.amount,
				'quantity_available': inventory_item[0].quantity,
			}
		item_no_enough.append(new_no_item)

	return item_no_exist, item_no_enough

def search_salesorder(model_all, form):

	model_list = model_all

	if form.cleaned_data['sapcode'] :
		status, model_list = utils.search_model(model_list, 'sapcode', form.cleaned_data['sapcode'], accept_all=True)

	if form.cleaned_data['project'] :
		status, model_list = utils.search_model(model_list, 'project', form.cleaned_data['project'], accept_all=True)

	if form.cleaned_data['detail'] :
		status, model_list = utils.search_model(model_list, 'detail', form.cleaned_data['detail'], accept_all=True)

	status = 0
	if len(model_list) == 0:
		status = -2

	return status, model_list

def search_saleorder_item(form, item_missing):
	#output = get_object_or_404(InventoryOutput, pk=output_pk)
	#output_saleorder_items = InventoryOutputItem.objects.filter(output=output.pk)
	#saleorder_items = SalesOrderItem.objects.filter(salesorder=output.sale_order)

	#item_missing = []

	#for sale_item in saleorder_items :
	#	item_exist = output_saleorder_items.filter(item_saleorder=sale_item)
	#	if not item_exist :
	#		item_missing.append(sale_item)

	#list_id = []
	#for item in item_missing :
	#	list_id.append(item.id)

	## Get model
	#model_list = saleorder_items.filter(pk__in=list_id)

	# Get salesorder items
	status_temp, saleorder_items = utils.search_model(item_missing, 'sap_code', form.cleaned_data['sap_code'], accept_all=True)

	if saleorder_items != {} :
		saleorder_items = saleorder_items.order_by('sap_code')

	# Valid search: 1 item in salesorder and inventory
	status = "no"

	# Only search in logistic/item
	if (3<len(saleorder_items)) or (saleorder_items=={}) :
		return status, saleorder_items, {}

	list_items = []
	for item in saleorder_items :
		inventory_item = Item.objects.filter(sap=item.sap_code)
		if inventory_item :
			list_items.append(inventory_item[0])

	# Valid item
	if (len(saleorder_items)==1) and (len(list_items)==1) :
		# Quantity is valid
		status = "quantity"
		if (saleorder_items[0].amount<=list_items[0].quantity) :
			status = "yes"

	return status, saleorder_items, list_items

def get_all_items(output_pk):
	output = get_object_or_404(InventoryOutput, pk=output_pk)
	output_saleorder_items = InventoryOutputItem.objects.filter(output=output.pk)
	saleorder_items = SalesOrderItem.objects.filter(salesorder=output.sale_order)

	item_missing = []

	for sale_item in saleorder_items :
		item_exist = output_saleorder_items.filter(item_saleorder=sale_item)
		if not item_exist :
			item_missing.append(sale_item)

	list_id = []
	for item in item_missing :
		list_id.append(item.id)

	# Get model
	item_missing = saleorder_items.filter(pk__in=list_id)

	context = {}
	context['output'] = output
	context['output_items'] = output_saleorder_items
	context['saleorder_items'] = item_missing

	return context, item_missing
