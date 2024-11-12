from django.contrib import admin
from .models import RequirementOrder, RequirementOrderItem

# Inline para los ítems de la orden de requerimiento
class RequirementOrderItemInline(admin.TabularInline):
    model = RequirementOrderItem
    extra = 1  # Número de ítems adicionales vacíos que se mostrarán
    min_num = 1  # Mínimo de ítems requeridos
    can_delete = True  # Permitir eliminar ítems

# Registro del modelo RequirementOrder con el inline de RequirementOrderItem
@admin.register(RequirementOrder)
class RequirementOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'sales_order', 'requested_date', 'created_at', 'estado', 'state', 'total_order')
    readonly_fields = ('order_number',)
    fields = ('sales_order', 'requested_date', 'created_at', 'notes', 'estado', 'user', 'total_order', 'purchase_order_created', 'state')
    inlines = [RequirementOrderItemInline]  # Añadimos el inline para gestionar ítems
    list_filter = ('state', 'purchase_order_created', 'created_at')
    search_fields = ('sales_order__sapcode', 'order_number')

# Registro opcional del modelo RequirementOrderItem (si quieres gestionarlo por separado)
@admin.register(RequirementOrderItem)
class RequirementOrderItemAdmin(admin.ModelAdmin):
    list_display = ('requirement_order', 'sales_order_item', 'quantity_requested', 'notes')
