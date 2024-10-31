from django.db import models

from client.models import Client

# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=255, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Proyecto"
        verbose_name_plural = "Proyectos"
