from django.contrib import admin
from .models import CommercialBudget, CommercialBudgetItem

# Registro básico de CommercialBudget y CommercialBudgetItem en el administrador
@admin.register(CommercialBudget)
class CommercialBudgetAdmin(admin.ModelAdmin):
    list_display = ('budget_name', 'client', 'budget_type', 'budget_date', 'budget_price', 'budget_final_price')
    search_fields = ('budget_name', 'client__name')
    list_filter = ('budget_type', 'budget_date')
    date_hierarchy = 'budget_date'

@admin.register(CommercialBudgetItem)
class CommercialBudgetItemAdmin(admin.ModelAdmin):
    list_display = ('budget', 'item', 'quantity', 'custom_price', 'total_price', 'unit')
    search_fields = ('item__description', 'budget__budget_name')
    list_filter = ('budget',)
