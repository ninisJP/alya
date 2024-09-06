from django.shortcuts import render

from .forms import ProjectForm
from .models import Project

def new_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'partials/success_project.html')
        return render(request, 'partials/failure_project.html')

    form = ProjectForm()
    context = {'form': form}
    return render(request, 'project_new.html', context)

def list_project(request):
    all_project = Project.objects.all().order_by('name')
    contex = {'projects': all_project}
    return render(request, 'project_list.html', contex)
