from django.shortcuts import render, redirect, get_object_or_404
from accounting_order_sales.models import PurchaseOrderItem, SalesOrder
from logistic_requirements.models import RequirementOrderItem

def project_order_plus(request, order_id):
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    sales_order_items = sales_order.items.all()
    
    requirement_orders_items = RequirementOrderItem.objects.filter(
        purchase_order_created=False,
        requirement_order__sales_order=sales_order,
        estado='L'  # Solo en estado 'Listo'
    )
    
    purchase_order_items = PurchaseOrderItem.objects.filter(
        purchaseorder__salesorder=sales_order
    )
    
    combined_items = list(requirement_orders_items) + list(purchase_order_items)

    # Acceder al proyecto y al cliente
    project = sales_order.project
    client = project.client if project else None

    # Creamos un diccionario para mapear la descripción (o SAP Code) al item
    sales_order_item_dict = {item.description: item for item in sales_order_items}

    # Ordenamos los ítems combinados de acuerdo al orden de los ítems en sales_order_items
    # Basado en la descripción o el código SAP
    combined_items.sort(key=lambda x: sales_order_item_dict.get(x.sales_order_item.description, None).id if x.sales_order_item.description in sales_order_item_dict else float('inf'))

    context = {
        'sales_order': sales_order,
        'sales_order_items': sales_order_items,
        'combined_items': combined_items,
        'project': project,
        'client': client,
    }
    
    return render(request, 'projectplus/project_order_plus.html', context)



