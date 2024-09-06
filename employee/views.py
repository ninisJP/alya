from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from follow_control_card.utils import create_monthly_cards_for_user
from django.shortcuts import render



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
        login(self.request, user)
        return super(RegisterView, self).form_valid(form)
    
    
# Render supervisor & technician
def supervisor_list_view(request):
    supervisors = Supervisor.objects.all()
    return render(request, 'list/list_supervisor.html', {'supervisors': supervisors})

def technician_list_view(request):
    technicians = Technician.objects.all()
    return render(request, 'list/list_technician.html', {'technicians': technicians})

