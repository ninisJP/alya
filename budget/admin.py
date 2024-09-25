from django.contrib import admin
from .models import Budget, CatalogItem, BudgetItem

# Registrar el modelo Item
admin.site.register(CatalogItem)

# Registrar el modelo BudgetItem
admin.site.register(BudgetItem)

# Registrar el modelo Budget con opciones adicionales
@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('budget_name', 'budget_days', 'budget_date', 'budget_final_price')
    search_fields = ('budget_name',)
    list_filter = ('budget_date',)
