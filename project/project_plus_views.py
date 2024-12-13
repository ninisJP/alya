from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from accounting_order_sales.models import PurchaseOrderItem, SalesOrder, PurchaseOrder
from logistic_inventory_input.models import InventoryInput
from logistic_inventory_inputnewitem.models import InventoryInputNewItem
from logistic_inventory_output.models import InventoryOutputItem
from logistic_requirements.models import RequirementOrderItem
from .forms import ProjectForm
from .models import Project
from itertools import chain

def project_order_plus(request, order_id):
    # Obtener la SalesOrder
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    
    # Obtener los ítems de SalesOrder
    sales_order_items = sales_order.items.all()
    
    # Filtrar los RequirementOrders de SalesOrder donde purchase_order_created es False
    requirement_orders = sales_order.requirement_orders.filter(purchase_order_created=False)
    
    # Obtener los PurchaseOrders asociados
    purchase_orders = sales_order.purchase_orders.all()
    
    # Obtener los ítems de RequirementOrder y PurchaseOrder
    requirement_order_items = RequirementOrderItem.objects.filter(requirement_order__in=requirement_orders)
    purchase_order_items = PurchaseOrderItem.objects.filter(purchaseorder__in=purchase_orders)
    
    # Combinamos los ítems de RequirementOrder y PurchaseOrder en una sola lista
    combined_items = list(chain(requirement_order_items, purchase_order_items))
    
    # Enviar los datos al template
    context = {
        'sales_order': sales_order,
        'sales_order_items': sales_order_items,
        'purchase_orders': purchase_orders,
        'requirement_orders': requirement_orders,
        'combined_items': combined_items,
    }
    
    return render(request, 'projectplus/project_order_plus.html', context)


