from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import TaskNote
from .forms import TaskNoteForm
from django.shortcuts import render, redirect

def task_wall(request):
    # Obtener todos los post-its creados
    tasks = TaskNote.objects.all()
    
    # Procesar el formulario de creación
    if request.method == 'POST':
        form = TaskNoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task-wall')  # Redirigir para evitar resubmission del formulario
    else:
        form = TaskNoteForm()
    
    # Pasar los post-its y el formulario al template
    return render(request, 'taskwall/task_wall.html', {'tasks': tasks, 'form': form})
