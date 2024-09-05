from django.db import models

# Create your models here.
class Client(models.Model):
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    tax_id = models.CharField(max_length=11, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    primary_contact = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name