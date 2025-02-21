# See LICENSE file for copyright and license details.
"""
Task Note views
"""
from django.shortcuts import render, redirect
from .models import TaskNote
from .forms import TaskNoteForm


def task_wall(request):
    """View to display Task Note"""
    tasks = TaskNote.objects.all()
    if request.method == 'POST':
        form = TaskNoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('task-wall')
    else:
        form = TaskNoteForm()
    context = {'tasks': tasks, 'form': form}
    return render(request, 'taskwall/task_wall.html', context)
