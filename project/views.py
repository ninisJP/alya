from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProjectForm
from .models import Project
from django.views.generic import ListView
from accounting_order_sales.models import SalesOrder
from django.db.models import Prefetch

def project_index(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            print('Proyecto guardado:', project)  # Confirma que el proyecto se guardó
            # Redirige a la misma vista para evitar duplicaciones y actualizar la lista
            return redirect('project_index')  # Cambia 'project_index' al nombre correcto de la URL
        else:
            print('Errores del formulario:', form.errors)
            return render(request, 'partials/project_failure.html', {'form': form})

    form = ProjectForm()
    context = {
        'form': form,
        'projects': Project.objects.all()
    }
    return render(request, 'project_index.html', context)

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
