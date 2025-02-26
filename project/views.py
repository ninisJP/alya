# See LICENSE file for copyright and license details.
"""
Project views
"""
from django.db.models import Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.db.models import Q


from accounting_order_sales.models import PurchaseOrderItem, SalesOrder
from logistic_inventory_input.models import InventoryInput
from logistic_inventory_inputnewitem.models import InventoryInputNewItem
from logistic_inventory_output.models import InventoryOutputItem
from logistic_requirements.models import RequirementOrderItem

from .forms import ProjectForm
from .models import Project


def project_index(request):
    """
    View to display the project index page
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            project = form.save()
            print('Proyecto guardado:', project)
            return redirect('project_index')
        else:
            print('Errores del formulario:', form.errors)
            return render(request, 'partials/project_failure.html', context)

    form = ProjectForm()
    projects_data = []

    # Recorre cada proyecto y calcula los totales de las órdenes de venta
    # pylint: disable=no-member
    for project in Project.objects.all():
        filtered_sales_orders = project.salesorder_set.filter(
            purchase_orders__scheduled_date__isnull=False
        ).distinct()

        # Calcular los totales del proyecto
        total_sales_sum = sum(
            order.total_sales_order for order in filtered_sales_orders)
        total_purchase_sum = sum(
            sum(
                purchase_order.total_purchase_order or 0 for purchase_order in order.purchase_orders.all())
            for order in filtered_sales_orders
        )
        total_utility_sum = sum(
            order.get_utility() for order in filtered_sales_orders)

        total_purchase_order_estimed_sum = sum(
            sum(purchase_order.total_purchase_order_estimed or 0 for purchase_order in order.purchase_orders.all())
            for order in filtered_sales_orders
        )

        projects_data.append({
            'project': project,
            'filtered_sales_orders': filtered_sales_orders,
            'total_sales_sum': total_sales_sum,
            'total_purchase_sum': total_purchase_sum,
            'total_utility_sum': total_utility_sum,
            'total_purchase_order_estimed_sum': (
                total_purchase_order_estimed_sum),
        })

    context = {
        'form': form,
        'projects_data': projects_data,
        'purchase_order_items': PurchaseOrderItem.objects.select_related(
            'sales_order_item').all()
    }
    return render(request, 'project_index.html', context)


def search_project(request):
    """
    Function to search for projects
    """
    # Obtener la consulta de búsqueda desde el request
    query = request.GET.get('q', '')

    # Si hay una búsqueda, filtrar los proyectos basados en la consulta
    if query:
        # pylint: disable=no-member
        projects = Project.objects.filter(
            Q(name__icontains=query)
        ).order_by('-id')
    else:
        # Mostrar todos los proyectos si no hay búsqueda
        # pylint: disable=no-member
        projects = Project.objects.all().order_by('-id')

    # Preparar los datos de los proyectos (similar a project_index)
    projects_data = []
    for project in projects:
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
        
        total_purchase_order_estimed_sum = sum(
            sum(purchase_order.total_purchase_order_estimed or 0 for purchase_order in order.purchase_orders.all())
            for order in filtered_sales_orders)
        
        projects_data.append({
            'project': project,
            'filtered_sales_orders': filtered_sales_orders,
            'total_sales_sum': total_sales_sum,
            'total_purchase_sum': total_purchase_sum,
            'total_utility_sum': total_utility_sum,
            'total_purchase_order_estimed_sum': total_purchase_order_estimed_sum,
        })

    context = {
        'projects_data': projects_data,
        'form': ProjectForm(),
        'purchase_order_items': PurchaseOrderItem.objects.select_related('sales_order_item').all()
    }

    # Devolver solo el fragmento de la lista
    return render(request, 'partials/project_list.html', context)

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

def diagram_project_orders(request, order_id):
    diagram = get_object_or_404(SalesOrder, id=order_id)
    return render(request, 'diagram/order_diagram.html', {'diagram': diagram})

