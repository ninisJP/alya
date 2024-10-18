from django.db import models
from django.contrib.auth.models import User


class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisors')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('medical_leave', 'Medical Leave'), ('retired', 'Retired')], default='active')
    email = models.EmailField(max_length=254)
    # dni = models.CharField(max_length=8, null=True, blank=True)


    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.position}'


class Technician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('medical_leave', 'Medical Leave'), ('retired', 'Retired')], default='active')
    email = models.EmailField(max_length=254)
    # dni = models.CharField(max_length=8, null=True, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} - {self.position} - {self.status}'
