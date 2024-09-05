from .models import *
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView
from employee.forms import *
from .forms import *
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import redirect

class Login(LoginView):
    template_name = 'registration/login.html'
    def form_valid(self, form):
        response = super().form_valid(form)
        
        return response
    

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super(RegisterView, self).form_valid(form)
    
    
