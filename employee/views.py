from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import login
from follow_control_card.utils import create_monthly_cards_for_user
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET
from django.db.models import Q

class Login(LoginView):
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        create_monthly_cards_for_user(self.request.user)
        return response
    

# class RegisterView(FormView):
#     template_name = 'registration/register.html'
#     form_class = UserRegistrationForm
#     success_url = reverse_lazy('partials/user_client.html')

#     def form_valid(self, form):
#         user = form.save()
#         login(self.request, user)
        
#         users = User.objects.exclude(username='admin')
#         context = {'user': user, 'users': users}
#         return render(self.request, 'register', context)

#     def form_invalid(self, form):
#         users = User.objects.exclude(username='admin')
#         return render(self.request, 'partials/failure_user.html', {'form': form, 'users': users})

#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         users = User.objects.exclude(username='admin')
#         context = {
#             'form': form,
#             'users': users,
#         }
#         return render(request, self.template_name, context)

class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('register')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        users = User.objects.exclude(username='admin')
        context = {'user': user, 'users': users}
        return render(self.request, 'partials/user_list.html', context)

    # def form_invalid(self, form):
    #     users = User.objects.exclude(username='admin')
    #     return render(self.request, 'partials/failure_user.html', {'form': form, 'users': users})
    
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

