from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import login
from follow_control_card.utils import create_monthly_cards_for_user
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.edit import UpdateView
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


class Login(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        create_monthly_cards_for_user(self.request.user)
        return response

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('register')

    def form_valid(self, form):
        user = form.save()
        users = User.objects.exclude(username='admin')
        context = {'users': users}
        return render(self.request, 'partials/user_list.html', context)

    
    def form_invalid(self, form):
        print(form.errors) 
        users = User.objects.exclude(username='admin')
        return render(self.request, 'partials/failure_user.html', {'form': form, 'users': users})

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        users = User.objects.exclude(username='admin')
        context = {
            'form': form,
            'users': users,
        }
        return render(request, self.template_name, context)


# Render supervisor & technician

def supervisor_list_view(request):
    supervisors = Supervisor.objects.all()
    return render(request, 'list/list_supervisor.html', {'supervisors': supervisors})

def technician_list_view(request):
    technicians = Technician.objects.all()
    return render(request, 'list/list_technician.html', {'technicians': technicians})


# Edit Supervisor & Technician
def edit_supervisor(request, pk):
    supervisor = get_object_or_404(Supervisor, pk=pk)
    if request.method == 'POST':
        form = SupervisorEditForm(request.POST, instance=supervisor)
        if form.is_valid():
            supervisor = form.save()
            return redirect('supervisor')
    else:
        form = SupervisorEditForm(instance=supervisor)
    
    return render(request, 'edit/edit_supervisor.html', {
        'form': form,
        'supervisor': supervisor
    })
    
def edit_technician(request, pk):
    technician = get_object_or_404(Technician, pk=pk)
    if request.method == 'POST':
        form = TechnicianEditForm(request.POST, instance=technician)
        if form.is_valid():
            technician = form.save()
            return redirect('technician')
    else:
        form = TechnicianEditForm(instance=technician)
    
    return render(request, 'edit/edit_technician.html', {
        'form': form,
        'technician': technician
    })