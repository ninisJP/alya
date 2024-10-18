from .models import InventoryOutput

from accounting_order_sales.models import SalesOrder, SalesOrderItem
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
