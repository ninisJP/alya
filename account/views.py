from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth import get_user_model
from accounts.forms import RegisterForm
from .utils import create_monthly_cards_for_user

class Login(LoginView):
    template_name = 'registration/login.html'
    def form_valid(self, form):
        response = super().form_valid(form)
        create_monthly_cards_for_user(self.request.user)
        return response

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save() 
        create_monthly_cards_for_user(user)
        return super().form_valid(form)
    
def check_username(request):
    username = request.POST.get('username')
    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse("<div style='color:red;'>Este trabajador esta registrado </div>")
    else:
        return HttpResponse("<div style='color:green;'>Este trabajador aun no esta registrado </div>")
