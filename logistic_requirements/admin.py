from django.contrib import admin
from .models import RequirementOrder,RequirementOrderItem

# Vista simplificada del modelo RequirementOrder sin inlines
@admin.register(RequirementOrder)
class RequirementOrderSimpleAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'sales_order', 'requested_date', 'created_at', 'estado', 'state', 'total_order')
    readonly_fields = ('order_number',)
    fields = ('sales_order', 'requested_date', 'created_at', 'notes', 'estado', 'user', 'total_order', 'purchase_order_created', 'state')
    list_filter = ('state', 'purchase_order_created', 'created_at')
    search_fields = ('sales_order__sapcode', 'order_number')

admin.site.register(RequirementOrderItem)
