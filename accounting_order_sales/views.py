from django.shortcuts import render
from .models import SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem,Bank,BankStatements
from .utils import procesar_archivo_excel
from .forms import SalesOrderForm, ItemSalesOrderExcelForm, ItemSalesOrderForm, BankForm,UploadBankStatementForm
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
import pandas as pd
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages



def salesorder(request):
    salesorders = SalesOrder.objects.all().order_by("-id")
    context = {'form': SalesOrderForm(), 'salesorders': salesorders} 
    return render(request, 'salesorder/sales_index.html', context)

def create_salesorder(request):
    if request.method == 'POST':
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            form.save()
            salesorders = SalesOrder.objects.all().order_by("-id")
            context = {'salesorders': salesorders}
            return render(request, 'salesorder/salesorder-list.html', context)
    else:
        form = SalesOrderForm()
    return render(request, 'salesorder/salesorder-form.html', {'form': form})

def edit_salesorder(request, salesorder_id):
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    if request.method == 'GET':
        form = SalesOrderForm(instance=salesorder)
        return render(request, 'salesorder/salesorder-edit.html', {'form': form, 'salesorder': salesorder})
    elif request.method == 'POST':
        form = SalesOrderForm(request.POST, instance=salesorder)
        if form.is_valid():
            form.save()
            salesorders = SalesOrder.objects.all().order_by("-id") 
            return render(request, 'salesorder/salesorder-list.html', {'salesorders': salesorders})
    return HttpResponse(status=405)

def delete_salesorder(request, salesorder_id):
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    if request.method == 'DELETE':
        salesorder.delete()
        salesorders = SalesOrder.objects.all().order_by("-id") 
        return render(request, 'salesorder/salesorder-list.html', {'salesorders': salesorders})
    return HttpResponse(status=405)

def items_salesorder(request, salesorder_id):
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    items = SalesOrderItem.objects.filter(salesorder=salesorder)

    if request.method == "POST":
        form = ItemSalesOrderForm(request.POST)
        excel_form = ItemSalesOrderExcelForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.salesorder = salesorder
            item.save()
            items = SalesOrderItem.objects.filter(salesorder=salesorder)
            return render(request, 'itemsalesorder/item-salesorder-list.html', {'items': items})

        if excel_form.is_valid():
            archivo_excel = request.FILES['archivo_excel']
            procesar_archivo_excel(archivo_excel, salesorder_id)
            items = SalesOrderItem.objects.filter(salesorder=salesorder)
            return render(request, 'itemsalesorder/item-salesorder-list.html', {'items': items})

    else:
        form = ItemSalesOrderForm()
        excel_form = ItemSalesOrderExcelForm()

    context = {
        'salesorder': salesorder,
        'items': items,
        'form': form,
        'excel_form': excel_form
    }

    return render(request, 'itemsalesorder/item-salesorder.html', context)

# Ordenes de compra
def purchase_orders(request, salesorder_id):
    # Obtener la SalesOrder correspondiente por su ID
    salesorder = get_object_or_404(SalesOrder, id=salesorder_id)
    # Filtrar todas las Purchase Orders relacionadas con esa SalesOrder
    purchase_orders = PurchaseOrder.objects.filter(salesorder=salesorder).prefetch_related('items')

    context = {
        'salesorder': salesorder,  # Pasar la Sales Order para referencia
        'purchase_orders': purchase_orders,  # Lista de Purchase Orders con sus Items
    }
    
    return render(request, 'purchaseorder/purchaseorder-list.html', context)


# Bank 
def index_bank(request):
    if request.method == 'POST':
        form = BankForm(request.POST)  
        if form.is_valid():
            print("Formulario válido. Banco:", form.cleaned_data.get('bank_name'))
            form.save()

            if request.headers.get('HX-Request'):  # Si es una petición HTMX
                context = {'banks': Bank.objects.all().order_by('-id')}
                return render(request, 'bank/bank_list.html', context)

            context = {'form': BankForm(), 'banks': Bank.objects.all()}
            return render(request, 'bank/bank_index.html', context)

        if request.headers.get('HX-Request'):  # Manejar los errores en HTMX
            return HttpResponse("Error en el formulario", status=400)

        return render(request, 'client/partials/failure_client.html')

    # En caso de GET request, mostrar el formulario vacío y la lista de bancos
    form = BankForm()
    context = {
        'form': form,
        'banks': Bank.objects.all().order_by('-id'),
        'pagina_activa': 'bancos'
    }
    return render(request, 'bank/bank_index.html', context)

def edit_bank(request, bank_id):
    bank = get_object_or_404(Bank, id=bank_id)
    
    if request.method == 'POST':
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            bank = form.save()

            if request.headers.get('HX-Request'):  # Si es una petición HTMX
                banks = Bank.objects.all().order_by('-id')
                return render(request, 'bank/bank_list.html', {'bank': bank, 'banks': banks})

            return redirect('bank_index')  

        if request.headers.get('HX-Request'):  # Manejar los errores en HTMX
            return HttpResponse("Error en el formulario", status=400)

        return render(request, 'client/partials/failure_client.html')

    # Corregir aquí asegurándonos de pasar el objeto `bank` al contexto
    form = BankForm(instance=bank)
    banks = Bank.objects.all().order_by('-id')  
    context = {
        'form': form,
        'banks': banks,
        'bank': bank  # Aquí estamos pasando la instancia de `bank`
    }
    return render(request, 'bank/bank_edit.html', context)


# Bank Delete
def delete_bank(request, bank_id):
    bank = get_object_or_404(Bank, id=bank_id)
    
    if request.method == 'POST':
        bank.delete()

        if request.headers.get('HX-Request'):  # Si es una petición HTMX
            return HttpResponse(status=204)  # Respuesta de éxito sin contenido

        return redirect('bank_index')  # Redirigir después de eliminar

    return render(request, 'bank/bank_delete.html', {'bank': bank})


# BankStatements
def bank_statements(request, bank_id):
    bank = get_object_or_404(Bank, pk=bank_id)
    statements = BankStatements.objects.filter(bank=bank)
    return render(request, 'bankstatement/BankStatements_list.html', {'bank': bank, 'statements': statements})

class BankStatementUploadView(FormView):
    template_name = 'bankstatement/upload_bank_statements.html'
    form_class = UploadBankStatementForm
    success_url = reverse_lazy('bank_index')  # Ajusta esto según tus necesidades

    def form_valid(self, form):
        # Obtener el banco seleccionado y el archivo del formulario
        bank = form.cleaned_data['bank']
        uploaded_file = self.request.FILES['excel_file']

        # Verificar que el archivo haya sido recibido
        print("Archivo recibido:", uploaded_file.name)

        try:
            # Intentar leer como CSV
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                print("Archivo CSV procesado correctamente.")
            # Intentar leer como Excel
            elif uploaded_file.name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(uploaded_file, engine='openpyxl')  # Especificar el motor openpyxl para archivos .xlsx
                print("Archivo Excel procesado correctamente.")
            else:
                raise ValueError("Formato de archivo no soportado.")

            # Mapeo de nombres de columnas
            column_mapping = {
                'F.Operac.': 'operation_date',
                'Referencia': 'reference',
                'Importe': 'amount',
                'ITF': 'itf',
                'Num.Mvto': 'number_moviment',
            }

            # Renombrar columnas y limpiar el DataFrame
            df.rename(columns=column_mapping, inplace=True)
            df = df[list(column_mapping.values())]

            # Crear BankStatements desde el DataFrame
            for _, row in df.iterrows():
                BankStatements.objects.create(
                    bank=bank,
                    operation_date=row['operation_date'],
                    reference=row['reference'],
                    amount=row['amount'],
                    itf=row['itf'],
                    number_moviment=row['number_moviment'],
                )

            # Mostrar un mensaje de éxito
            messages.success(self.request, 'Extractos bancarios subidos exitosamente.')
        except Exception as e:
            print("Error procesando archivo:", e)
            messages.error(self.request, 'Hubo un error procesando el archivo. Por favor, revisa el formato.')

        return super().form_valid(form)