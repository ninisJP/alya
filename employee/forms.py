from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Supervisor, Technician

class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('supervisor', 'Supervisor'),
        ('technician', 'Técnico'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Cargo')
    first_name = forms.CharField(max_length=100, required=True, label='Nombre')
    last_name = forms.CharField(max_length=100, required=True, label='Apellido')
    position = forms.CharField(max_length=100, required=True, label='Posición')
    email = forms.EmailField(max_length=254, required=True, label='Correo Electrónico')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role', 'position']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            role = self.cleaned_data['role']
            if role == 'supervisor':
                Supervisor.objects.create(
                    user=user,
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    position=self.cleaned_data['position'],
                    email=self.cleaned_data['email'],
                )
            else:
                Technician.objects.create(
                    user=user,
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    position=self.cleaned_data['position'],
                    email=self.cleaned_data['email'],
                )
        return user
