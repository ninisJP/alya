from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView

from employee.forms import RegisterForm

from .models import *

from follow_control_card.utils import create_monthly_cards_for_user


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
        return super().form_valid(form)
