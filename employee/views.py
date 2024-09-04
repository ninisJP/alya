from .models import *
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView
from employee.forms import RegisterForm


class Login(LoginView):
    template_name = 'registration/login.html'
    def form_valid(self, form):
        response = super().form_valid(form)
        
        return response
    
    
class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save() 
        return super().form_valid(form)