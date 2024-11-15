import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Budget, BudgetItem
from django.conf import settings
import pandas as pd
from decimal import Decimal
from .models import CatalogItem

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

def process_budget_excel(excel_file, budget_id):
    # Obtener la instancia de Budget por su ID
    budget = Budget.objects.get(id=budget_id)

    # Procesar el archivo Excel
    xls = pd.ExcelFile(excel_file)
    if 'listado' not in xls.sheet_names:
        raise ValueError("El archivo no contiene una hoja llamada 'listado'.")

    # Leer la hoja "listado" del archivo Excel
    df = pd.read_excel(xls, sheet_name='listado')

    # Verificar que las columnas esperadas existan
    expected_columns = ['DESCRIPCION DE PARTIDA', 'UND', 'CANT.', 'P.U.']
    if not all(col in df.columns for col in expected_columns):
        raise ValueError("El archivo Excel no tiene el formato esperado.")

    # Iterar sobre cada fila y procesar los datos
    for index, row in df.iterrows():
        description = row['DESCRIPCION DE PARTIDA']
        unit = row['UND']
        quantity = row['CANT.']
        custom_price = row['P.U.']

        # Buscar el ítem en el catálogo por coincidencia exacta
        catalog_item = CatalogItem.objects.filter(description__iexact=description).first()

        # Si encuentra una coincidencia exacta, crear el BudgetItem
        if catalog_item:
            BudgetItem.objects.create(
                budget=budget,
                item=catalog_item,
                quantity=quantity,
                custom_price=custom_price,
                custom_price_per_day=catalog_item.price_per_day,  # Si es necesario
                unit=unit
            )
        else:
            # Si no se encuentra coincidencia exacta, continuar con el siguiente ítem
            print(f"No se encontró el ítem exacto para: {description}")
            continue

def determine_category(sap_code):
    """Determina la categoría del ítem basado en las primeras letras del código SAP."""
    if sap_code.startswith('HER'):
        return CatalogItem.Category.HERRAMIENTA
    elif sap_code.startswith('CON'):
        return CatalogItem.Category.CONSUMIBLE
    elif sap_code.startswith('MOB'):
        return CatalogItem.Category.MANODEOBRA
    elif sap_code.startswith('MAT'):
        return CatalogItem.Category.MATERIAL
    elif sap_code.startswith('EPPS'):
        return CatalogItem.Category.EPPS
    elif sap_code.startswith('EQU'):
        return CatalogItem.Category.EQUIPO
    else:
        return CatalogItem.Category.EQUIPO  # Asignar una categoría por defecto si no coincide

from decimal import Decimal
import pandas as pd

def process_sap_excel(excel_file, budget):
    import pandas as pd
    from decimal import Decimal
    from django.db import transaction

    # Procesar el archivo Excel
    xls = pd.ExcelFile(excel_file)
    if 'listado' not in xls.sheet_names:
        raise ValueError("El archivo no contiene una hoja llamada 'listado'.")

    # Leer la hoja "listado" del archivo Excel
    df = pd.read_excel(xls, sheet_name='listado')

    # Verificar que las columnas esperadas existan
    expected_columns = ['Número de artículo', 'Descripción del artículo', 'Nombre de unidad de medida', 'Cantidad', 'Precio por unidad', 'Total (ML)']
    if not all(col in df.columns for col in expected_columns):
        raise ValueError("El archivo Excel no tiene el formato esperado.")

    # **Lista para almacenar los códigos SAP presentes en el Excel**
    sap_codes_in_excel = set()

    # Iniciar una transacción atómica
    with transaction.atomic():
        # Iterar sobre cada fila y procesar los datos
        for index, row in df.iterrows():
            sap_code = row['Número de artículo']

            # Verificar si el código SAP es válido (no nulo)
            if pd.isna(sap_code) or pd.isnull(sap_code):
                print(f"Fila {index} sin código SAP. Saltando esta fila.")
                continue

            sap_code = str(sap_code).strip()  # Asegurarse de que es una cadena sin espacios
            sap_codes_in_excel.add(sap_code)  # Agregar el código SAP a la lista

            description = row['Descripción del artículo']
            unit = row['Nombre de unidad de medida']

            try:
                # Manejar cantidad (quantity)
                quantity = Decimal(row['Cantidad']) if not pd.isna(row['Cantidad']) else Decimal(0)

                # Manejar custom_price (Precio por unidad)
                custom_price_value = row['Precio por unidad']
                if isinstance(custom_price_value, str):
                    custom_price = Decimal(custom_price_value.replace('S/', '').strip())
                elif isinstance(custom_price_value, (float, int)):
                    custom_price = Decimal(custom_price_value)
                else:
                    custom_price = Decimal(0)

                # Manejar total_price (Total)
                total_price_value = row['Total (ML)']
                if isinstance(total_price_value, str):
                    total_price = Decimal(total_price_value.replace('S/', '').strip())
                elif isinstance(total_price_value, (float, int)):
                    total_price = Decimal(total_price_value)
                else:
                    total_price = Decimal(0)

            except Exception as e:
                print(f"Error al convertir los valores numéricos en la fila {index}: {str(e)}")
                continue  # Saltar esta fila si hay un error de conversión

            # Buscar el ítem en el catálogo por su código SAP o crear uno nuevo
            try:
                catalog_item = CatalogItem.objects.get(sap=sap_code)
                # Verificar y actualizar la descripción si es diferente
                if catalog_item.description != description:
                    catalog_item.description = description
                    catalog_item.save()
                    print(f"Descripción del SAP {sap_code} actualizada a '{description}'.")
            except CatalogItem.DoesNotExist:
                print(f"No se encontró el ítem con SAP {sap_code}. Creando uno nuevo.")
                category = determine_category(sap_code)  # Asumimos que tienes esta función
                catalog_item = CatalogItem.objects.create(
                    sap=sap_code,
                    description=description,
                    unit=unit,
                    price=custom_price,
                    price_per_day=custom_price / Decimal(30) if custom_price else Decimal(0),  # Evitar división por cero
                    category=category
                )

            # Obtener o crear un nuevo BudgetItem
            budget_item, created = BudgetItem.objects.get_or_create(
                budget=budget,
                item=catalog_item,
            )

            # Actualizar los campos del BudgetItem
            budget_item.quantity = quantity
            budget_item.custom_price = custom_price
            budget_item.unit = unit
            budget_item.total_price = total_price

            # Guardar el BudgetItem para que se ejecuten los cálculos en el método save()
            budget_item.save()

            if created:
                print(f"Se ha creado un nuevo BudgetItem para el SAP {sap_code}.")
            else:
                print(f"Se ha actualizado el BudgetItem existente para el SAP {sap_code}.")

        # **Después de procesar todos los ítems, eliminar los BudgetItems que ya no están en el Excel**
        # Obtener los códigos SAP de los BudgetItems actuales en el presupuesto
        current_sap_codes = set(budget.items.values_list('item__sap', flat=True))

        # Identificar los códigos SAP que deben eliminarse
        sap_codes_to_delete = current_sap_codes - sap_codes_in_excel

        if sap_codes_to_delete:
            # Eliminar los BudgetItems cuyo código SAP está en sap_codes_to_delete
            items_to_delete = budget.items.filter(item__sap__in=sap_codes_to_delete)
            items_to_delete.delete()
            print(f"Se han eliminado {items_to_delete.count()} BudgetItems que ya no están en el Excel.")
        else:
            print("No hay BudgetItems para eliminar.")

