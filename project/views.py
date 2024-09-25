from django.shortcuts import render

from .forms import ProjectForm
from .models import Project


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
