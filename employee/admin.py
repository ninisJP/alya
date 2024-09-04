# employee_supervisor_db/admin.py

from django.contrib import admin
from .models import *

@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'supervisor_position', 'status', 'email')
    search_fields = ('first_name', 'last_name', 'position', 'email')
    list_filter = ('status',)

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'

    def supervisor_position(self, obj):
        return f"Supervisor {obj.position}"
    supervisor_position.short_description = 'Position'

    
    
@admin.register(Technical)
class TechnicalAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'technical_position', 'status', 'email')
    search_fields = ('first_name', 'last_name', 'position', 'email')
    list_filter = ('status',)
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'

    def technical_position(self, obj):
        return f"Técnico {obj.position}"
    technical_position.short_description = 'Position'