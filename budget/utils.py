import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Budget, BudgetItem
from django.conf import settings

def export_budget_report_to_excel(request, pk):
    budget = get_object_or_404(Budget, pk=pk)

    # Cargar la plantilla de Excel
    file_path = f'{settings.BASE_DIR}/static/plantilla.xlsx'
    plantilla = openpyxl.load_workbook(file_path)

    # Agrupar los ítems por categoría (content_type)
    items_by_category = {}
    for item in budget.items.all():
        categoria = item.item.category
        if categoria not in items_by_category:
            items_by_category[categoria] = []
        items_by_category[categoria].append(item)

    # Crear una hoja para cada categoría de ítem
    for categoria, items in items_by_category.items():
        ws_categoria = plantilla.create_sheet(title=f"{categoria}")
        _crear_hoja_presupuesto(ws_categoria, budget, {categoria: items}, simbolo='S/')

    # Crear una hoja final con el resumen de todos los ítems y valores finales
    ws_resumen = plantilla.create_sheet(title="Resumen Final")
    _crear_hoja_resumen(ws_resumen, budget, items_by_category)

    # Crear la hoja de cotización
    _create_quote(plantilla, budget)

    # Crear la respuesta HTTP con el nombre del archivo según el nombre del presupuesto
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="cotizacion_{budget.budget_name}.xlsx"'
    plantilla.save(response)

    return response

def _crear_hoja_presupuesto(ws, budget, items_by_category, simbolo='S/'):
    # Estilos generales
    header_font = Font(name="Calibri", bold=True, size=12, color="FFFFFF")
    cell_font = Font(name="Calibri", size=11)
    alignment_center = Alignment(horizontal="center", vertical="center")
    fill_blue = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Título del presupuesto
    ws['A1'] = f'PRESUPUESTO: {budget.budget_name} ({simbolo})'
    ws['A1'].font = Font(bold=True, size=16, name="Calibri")
    ws['A1'].alignment = alignment_center

    # Encabezados de la tabla
    headers = ['ITEM', 'DESCRIPCION DE ITEM', 'CATEGORÍA', 'CANTIDAD', 'PRECIO UNITARIO', 'SUBTOTAL']
    ws.append(headers)
    for cell in ws[2]:  # Segunda fila
        cell.font = header_font
        cell.fill = fill_blue
        cell.alignment = alignment_center
        cell.border = thin_border

    # Datos de los ítems
    for items in items_by_category.values():
        for item in items:
            subtotal = item.total_price
            row = [
                item.item.sap,
                item.item.description,
                item.item.category,
                item.quantity,
                item.item.price,
                subtotal
            ]
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.font = cell_font
                cell.alignment = alignment_center
                cell.border = thin_border

    # Añadir el resumen financiero al final
    ws.append([''])
    resumen = [
        ('TOTAL PARCIAL', f'{simbolo} {budget.budget_price:.2f}'),
        ('GASTOS ADMINISTRATIVOS', f'{simbolo} {budget.budget_expenses:.2f}'),
        ('UTILIDAD', f'{simbolo} {budget.budget_utility:.2f}'),
        ('TOTAL FINAL', f'{simbolo} {budget.budget_final_price:.2f}')
    ]

    for label, value in resumen:
        ws.append([label, '', '', '', '', value])
        for cell in ws[ws.max_row]:
            cell.font = cell_font if label != 'TOTAL FINAL' else Font(bold=True, size=12, color="FF0000")
            cell.alignment = alignment_center
            cell.border = thin_border
            if label == 'TOTAL FINAL':
                cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    # Ajustar ancho de las columnas
    for column in ws.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value)  # Evitar valores vacíos
        adjusted_width = max_length + 2
        ws.column_dimensions[column[0].column_letter].width = adjusted_width

def _crear_hoja_resumen(ws, budget, items_by_category):
    # Estilos generales
    header_font = Font(name="Calibri", bold=True, size=12, color="FFFFFF")
    cell_font = Font(name="Calibri", size=11)
    alignment_center = Alignment(horizontal="center", vertical="center")
    fill_blue = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Título del resumen
    ws['A1'] = f'RESUMEN FINAL DEL PRESUPUESTO: {budget.budget_name}'
    ws['A1'].font = Font(bold=True, size=16, name="Calibri")
    ws['A1'].alignment = alignment_center

    # Encabezados de la tabla
    headers = ['ITEM', 'DESCRIPCIÓN', 'CATEGORÍA', 'CANTIDAD', 'PRECIO UNITARIO', 'SUBTOTAL']
    ws.append(headers)
    for cell in ws[2]:
        cell.font = header_font
        cell.fill = fill_blue
        cell.alignment = alignment_center
        cell.border = thin_border

    # Listado de todos los ítems agrupados por categoría
    for categoria, items in items_by_category.items():
        ws.append([categoria])  # Título de categoría
        for item in items:
            subtotal = item.total_price
            row = [
                item.item.sap,
                item.item.description,
                item.item.category,
                item.quantity,
                item.item.price,
                subtotal
            ]
            ws.append(row)
            for cell in ws[ws.max_row]:
                cell.font = cell_font
                cell.alignment = alignment_center
                cell.border = thin_border

    # Añadir el resumen financiero al final
    ws.append([''])
    resumen = [
        ('TOTAL PARCIAL', f'S/ {budget.budget_price:.2f}'),
        ('GASTOS ADMINISTRATIVOS', f'S/ {budget.budget_expenses:.2f}'),
        ('UTILIDAD', f'S/ {budget.budget_utility:.2f}'),
        ('TOTAL FINAL', f'S/ {budget.budget_final_price:.2f}')
    ]

    for label, value in resumen:
        ws.append([label, '', '', '', '', value])
        for cell in ws[ws.max_row]:
            cell.font = cell_font if label != 'TOTAL FINAL' else Font(bold=True, size=12, color="FF0000")
            cell.alignment = alignment_center
            cell.border = thin_border
            if label == 'TOTAL FINAL':
                cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    # Ajustar ancho de las columnas
    for column in ws.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value)  # Evitar valores vacíos
        adjusted_width = max_length + 2
        ws.column_dimensions[column[0].column_letter].width = adjusted_width

def _create_quote(plantilla, budget):
    sheet = plantilla['COTIZACION']
    # Datos del cliente
    sheet['C18'] = f'{budget.client}'
    sheet['C19'] = f'{budget.client.primary_contact}'
    sheet['C20'] = f'{budget.client.email}'
    sheet['C21'] = f'{budget.client.phone}'

    # Información del presupuesto
    sheet['G20'] = f'{budget.budget_number}'
    sheet['G21'] = f'{budget.budget_date}'

    # Detalles de la cotización
    sheet['C27'] = f'{budget.budget_name}'
    sheet['G30'] = f'{budget.budget_final_price}'

    # Tiempos
    sheet['D35'] = f'{budget.budget_deliverytime}'
    sheet['D36'] = f'{budget.budget_servicetime}'
    sheet['D38'] = f'{budget.budget_warrantytime}'
