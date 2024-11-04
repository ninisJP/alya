from django.shortcuts import get_object_or_404

from datetime import datetime

from accounting_order_sales.models import PurchaseOrder, PurchaseOrderItem
from budget.models import CatalogItem
from logistic_inventory.models import Item

from .models import InventoryInputNewItem

def get_all_purchase():
	# Get valid by date Purchase Order
	purchase_items_all = PurchaseOrderItem.objects.all()
	today = datetime.today().date()

	list_temp_purchase = []
	for item in purchase_items_all :
		if item.purchaseorder.scheduled_date <= today:
			item_exist = InventoryInputNewItem.objects.filter(purchase_item=item)
			if not item_exist :
				list_temp_purchase.append(item.purchaseorder.pk)

	list_temp_purchase = set(list_temp_purchase)
	print(list_temp_purchase)
	list_purchase = PurchaseOrder.objects.filter(pk__in=list_temp_purchase)

	return list_purchase

def get_all_items(purchase_pk):
	purchase = get_object_or_404(PurchaseOrder, pk=purchase_pk)
	purchase_items_all = PurchaseOrderItem.objects.filter(purchaseorder=purchase)

	list_id = []
	list_miss_id = []
	list_error_id = []
	for item in purchase_items_all :
		# Input exist
		item_exist = InventoryInputNewItem.objects.filter(purchase_item=item)
		if item_exist :
			continue

		# Catalog and valid
		item_catalog = CatalogItem.objects.filter(sap=item.sap_code)
		if item_catalog :
			item_inventory = Item.objects.filter(item=item_catalog[0])
			if item_inventory :
				list_id.append(item.pk)
			else :
				list_miss_id.append(item.pk)
		else :
			list_error_id.append(item.pk)

	purchase_items = PurchaseOrderItem.objects.filter(pk__in=list_id)
	purchase_miss_items = PurchaseOrderItem.objects.filter(pk__in=list_miss_id)
	purchase_error_items = PurchaseOrderItem.objects.filter(pk__in=list_error_id)

	context = {}
	context['purchase'] = purchase
	context['purchase_items'] = purchase_items
	context['purchase_miss_items'] = purchase_miss_items
	context['purchase_error_items'] = purchase_error_items
	return context, purchase_items

def new_item(purchase_item_pk, quantity):
	status = "no"
	purchase_item = get_object_or_404(PurchaseOrderItem, pk=purchase_item_pk)
	item_catalog = get_object_or_404(CatalogItem, sap=purchase_item.sap_code)
	inventory_item = get_object_or_404(Item, item=item_catalog)

	# Quantity valid
	if quantity<1 :
		return status

	# Create Input
	input_item = InventoryInputNewItem(
			purchase_item = purchase_item,
			quantity = quantity
			)
	input_item.save();

	inventory_item.quantity = inventory_item.quantity + quantity
	inventory_item.save()

	status = "yes"

	return status
