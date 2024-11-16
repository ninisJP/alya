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

def project_index(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            print('Proyecto guardado:', project)
            return redirect('project_index')
        else:
            print('Errores del formulario:', form.errors)
            return render(request, 'partials/project_failure.html', {'form': form})

    form = ProjectForm()
    projects_data = []

    # Recorre cada proyecto y calcula los totales de las órdenes de venta
    for project in Project.objects.all():
        filtered_sales_orders = project.salesorder_set.filter(
            purchase_orders__scheduled_date__isnull=False
        ).distinct()

        # Calcular los totales del proyecto
        total_sales_sum = sum(order.total_sales_order for order in filtered_sales_orders)
        total_purchase_sum = sum(
            sum(purchase_order.total_purchase_order or 0 for purchase_order in order.purchase_orders.all())
            for order in filtered_sales_orders
        )
        total_utility_sum = sum(order.get_utility() for order in filtered_sales_orders)

        projects_data.append({
            'project': project,
            'filtered_sales_orders': filtered_sales_orders,
            'total_sales_sum': total_sales_sum,
            'total_purchase_sum': total_purchase_sum,
            'total_utility_sum': total_utility_sum
        })

    context = {
        'form': form,
        'projects_data': projects_data,
        'purchase_order_items': PurchaseOrderItem.objects.select_related('sales_order_item').all()
    }
    return render(request, 'project_index.html', context)

def sales_order_detail(request, order_id):
    # Obtener la orden de venta específica y sus ítems
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    items = sales_order.items.all()  # Relación de `SalesOrderItem` con `SalesOrder`
    #
    # Pasar la orden y los ítems al contexto
    context = {
        'sales_order': sales_order,
        'items': items,
    }
    return render(request, 'projects/sales_order_detail.html', context)

def sales_order_partial_view(request, order_id):
    # Obtener la orden de venta específica
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    items = sales_order.items.all()  # Relación de `SalesOrderItem` con `SalesOrder`

    # Pasar la orden y los ítems al contexto
    context = {
        'sales_order': sales_order,
        'items': items,
    }
    return render(request, 'partials/sales_order_partial.html', context)

def purchase_order_partial_view(request, order_id):
    # Obtener la orden de venta y sus órdenes de compra relacionadas
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    purchase_orders = sales_order.purchase_orders.all()  # Relación inversa de SalesOrder a PurchaseOrder

    context = {
        'purchase_orders': purchase_orders,
    }
    return render(request, 'partials/purchase_order_partial.html', context)

def requirement_order_partial_view(request, order_id):
    # Obtener la orden de venta y sus órdenes de requerimiento relacionadas
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    requirement_orders = sales_order.requirement_orders.all()  # Relación inversa de SalesOrder a RequirementOrder

    context = {
        'requirement_orders': requirement_orders,
    }
    return render(request, 'partials/requirement_order_partial.html', context)

class ProjectSalesOrderListView(ListView):
    model = Project
    template_name = 'projects/project_sales_order_list.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Accedemos a las órdenes de venta relacionadas para cada proyecto
        for project in context['projects']:
            project.sales_orders = project.salesorder_set.all()
        print('Lista de proyectos con órdenes de venta cargada')
        return context

    def get_queryset(self):
        # Prefetch para optimizar las consultas de órdenes de venta asociadas
        return Project.objects.prefetch_related(
            Prefetch('salesorder_set', queryset=SalesOrder.objects.all())
        )

def input_guide_partial_view(request, order_id):
    # Obtener la orden de venta y sus órdenes de compra relacionadas
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    items_sale_order = sales_order.items.all()
    list_item_input = []
    for item in items_sale_order :
        # Get requirement
        item_requirement = RequirementOrderItem.objects.filter(sales_order_item=item)
        if not item_requirement :
            continue
        # Get OutputItem
        item_output = InventoryOutputItem.objects.filter(item_requirement=item_requirement[0])
        if not item_output :
            continue
        # Get InputItem
        item_input = InventoryInput.objects.filter(output_item=item_output[0])
        if item_output :
            list_item_input.append(item_input[0])

    context = {}
    context['input_items'] = list_item_input
    return render(request, 'partials/input_guide_partial.html', context)

def saleorder_input_guide_partial_view(request, order_id):
    # Obtener la orden de venta y sus órdenes de compra relacionadas
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    items_sale_order = sales_order.items.all()

    list_item_input = []
    for item in items_sale_order :
        item_purchase = PurchaseOrderItem.objects.filter(sales_order_item=item)
        if not item_purchase :
            continue
        item_input = InventoryInputNewItem.objects.filter(purchase_item=item_purchase[0])
        if item_input :
            list_item_input.append(item_input[0])
    context = {}
    context['input_items'] = list_item_input
    return render(request, 'partials/saleorder_input_guide_partial.html', context)

def output_guide_partial_view(request, order_id):
    # Obtener la orden de venta y sus órdenes de compra relacionadas
    sales_order = get_object_or_404(SalesOrder, id=order_id)
    items_sale_order = sales_order.items.all()
    list_item_output = []
    for item in items_sale_order :
        item_requirement = RequirementOrderItem.objects.filter(sales_order_item=item)
        if not item_requirement :
            continue
        item_output = InventoryOutputItem.objects.filter(item_requirement=item_requirement[0])
        if item_output :
            list_item_output.append(item_output[0])

    context = {}
    context['output_items'] = list_item_output
    return render(request, 'partials/output_guide_partial.html', context)
