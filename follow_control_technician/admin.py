from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(TechnicianCardTask)
admin.site.register(TechnicianCard)
admin.site.register(TechnicianTask)
admin.site.register(TechnicianTaskGroup)
admin.site.register(TechnicianTaskGroupItem)