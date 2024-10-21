from .models import InventoryOutput

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

def search_salesorder_item(form):
	# Get salesorder items
	status_temp, saleorder_items = utils.search_model(SalesOrderItem.objects.all(), 'sap_code', form.cleaned_data['sap_code'], accept_all=True)

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

	if (len(saleorder_items)==1) and (len(list_items)==1) :
		status = "yes"

	return status, saleorder_items, list_items
