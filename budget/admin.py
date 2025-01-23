# See LICENSE file for copyright and license details.
"""
Models budget to see by admin
"""
from django.contrib import admin

from .models import Budget, CatalogItem, BudgetItem

admin.site.register(CatalogItem)
admin.site.register(BudgetItem)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """
    Admin can see the budget model.
    """

    list_display = (
        'budget_name',
        'budget_days',
        'budget_date',
        'budget_final_price'
    )
    search_fields = ('budget_name',)
    list_filter = ('budget_date',)
