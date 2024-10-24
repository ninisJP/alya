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
    dni = forms.CharField(max_length=8,required=True,label='DNI')
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name','dni','role', 'position','password1', 'password2']

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
                    dni=self.cleaned_data['dni'],
                    position=self.cleaned_data['position'],
                    email=self.cleaned_data['email'],
                )
            elif role == 'technician':
                Technician.objects.create(
                    user=user,
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    dni=self.cleaned_data['dni'],
                    position=self.cleaned_data['position'],
                    email=self.cleaned_data['email'],
                )
        return user


class SupervisorEditForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('supervisor', 'Supervisor'),
        ('technician', 'Técnico'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Cargo', initial='supervisor')

    class Meta:
        model = Supervisor
        fields = ['first_name', 'last_name', 'position', 'status', 'email', 'dni', 'role']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'position': 'Posición',
            'status': 'Estado',
            'email': 'Correo Electrónico',
            'dni': 'DNI',
            'role': 'Cargo',
        }

    def save(self, commit=True):
        supervisor = super(SupervisorEditForm, self).save(commit=False)
        if commit:
            supervisor.save()
            role = self.cleaned_data['role']
            if role == 'technician':
                Technician.objects.create(
                    user=supervisor.user,
                    first_name=supervisor.first_name,
                    last_name=supervisor.last_name,
                    dni=supervisor.dni,
                    position=supervisor.position,
                    email=supervisor.email,
                )
                supervisor.delete()
        return supervisor

class TechnicianEditForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('supervisor', 'Supervisor'),
        ('technician', 'Técnico'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Cargo', initial='technician')

    class Meta:
        model = Technician
        fields = ['first_name', 'last_name', 'position', 'status', 'email', 'dni', 'role']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'position': 'Posición',
            'status': 'Estado',
            'email': 'Correo Electrónico',
            'dni': 'DNI',
            'role': 'Cargo',
        }

    def save(self, commit=True):
        technician = super(TechnicianEditForm, self).save(commit=False)
        if commit:
            technician.save()
            role = self.cleaned_data['role']
            if role == 'supervisor':
                Supervisor.objects.create(
                    user=technician.user,
                    first_name=technician.first_name,
                    last_name=technician.last_name,
                    dni=technician.dni,
                    position=technician.position,
                    email=technician.email,
                )
                technician.delete()
        return technician