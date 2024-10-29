from django.shortcuts import render
from .forms import ProjectForm
from .models import Project
from django.views.generic import ListView

def project_index(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            context = {'project': project}
            return render(request, 'partials/project_list.html', context)
        return render(request, 'partials/project_failure.html')

    form = ProjectForm()
    context = {'form': form, 'projects': Project.objects.all()}
    return render(request, 'project_index.html', context)

class ProjectSalesOrderListView(ListView):
    model = Project
    template_name = 'projects/project_sales_order_list.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Accedemos a las órdenes de venta sin asignar relaciones inversas
        for project in context['projects']:
            project.sales_orders = project.salesorder_set.all()
        return context

