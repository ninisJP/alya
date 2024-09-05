from django.shortcuts import render

from .forms import ProjectForm

# Create your views here.
def index(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'partials/success_project.html')
        return render(request, 'partials/failure_project.html')

    form = ProjectForm()
    context = {'form': form}
    return render(request, 'project_index.html', context)
