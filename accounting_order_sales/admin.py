from django.contrib import admin
from .models import SalesOrder, SalesOrderItem,Bank, BankStatements
# Inline para los ítems de la orden de venta
class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 1  # Cuántos ítems adicionales vacíos mostrar por defecto
    min_num = 1  # Mínimo de ítems requeridos
    can_delete = True  # Permitir eliminar ítems

# Registro del modelo SalesOrder con el inline de SalesOrderItem
@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('sapcode', 'project', 'detail', 'date')  # Campos que se mostrarán en la lista
    inlines = [SalesOrderItemInline]  # Añadimos el inline para gestionar los ítems desde la orden

# Registro del modelo SalesOrderItem (opcional si quieres gestionarlo también por separado)
@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(admin.ModelAdmin):
    list_display = ('salesorder', 'sap_code', 'description', 'amount', 'price', 'price_total')
    
admin.site.register(Bank)
admin.site.register(BankStatements)


