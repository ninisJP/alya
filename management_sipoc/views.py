from django.shortcuts import render, get_object_or_404, redirect
from .models import SIPOC, SIPOCRow
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.http import HttpResponse
from .forms import (
    SIPOCForm, 
    SIPOCRowForm,
    SupplierForm, 
    InputForm, 
    ProcessForm, 
    OutputForm, 
    CustomerForm,
    SIPOCRowSuppliersForm,
    SIPOCRowInputsForm,
    SIPOCRowProcessesForm,
    SIPOCRowOutputsForm,
    SIPOCRowCustomersForm,
)


def list_sipocs(request):
    sipocs = SIPOC.objects.all()
    form = SIPOCForm()  # Inicializar el formulario para el modal
    return render(request, 'index_management_sipoc.html', {'sipocs': sipocs, 'form': form})

def create_sipoc(request):
    if request.method == 'POST':
        form = SIPOCForm(request.POST)
        if form.is_valid():
            sipoc = form.save()
            messages.success(request, "SIPOC creado con éxito. Ahora puedes agregar filas.")
            return redirect('detail_sipoc', sipoc_id=sipoc.id)  # Redirige a la vista de detalle
        else:
            messages.error(request, "Hubo un error al crear el SIPOC. Revisa los datos e inténtalo de nuevo.")
    else:
        form = SIPOCForm()
    
    # Renderizar de nuevo la lista de SIPOCs en caso de error
    sipocs = SIPOC.objects.all()
    return render(request, 'management/index_management_sipoc.html', {'sipocs': sipocs, 'form': form})

def detail_sipoc(request, sipoc_id):
    sipoc = get_object_or_404(SIPOC, id=sipoc_id)
    rows = sipoc.rows.all()  # Obtener todas las filas asociadas

    form = SIPOCRowForm()  # Formulario para agregar una nueva fila

    return render(request, 'sipoc/detail_sipoc.html', {'sipoc': sipoc, 'rows': rows, 'form': form})

def add_row(request, sipoc_id):
    sipoc = get_object_or_404(SIPOC, id=sipoc_id)

    if request.method == 'POST':
        form = SIPOCRowForm(request.POST)
        if form.is_valid():
            row = form.save(commit=False)
            row.sipoc = sipoc
            row.save()
            form.save_m2m()

            # Obtener todas las filas actualizadas
            rows = sipoc.rows.all()

            # Renderizar todas las filas en una cadena
            rows_html = ''
            for r in rows:
                rows_html += render_to_string('sipoc/_row.html', {'row': r})

            return HttpResponse(rows_html)
        else:
            # Renderizar el formulario con errores
            form_html = render_to_string('sipoc/add_row_form.html', {'form': form, 'sipoc': sipoc})
            return HttpResponse(form_html, status=400)
    else:
        # Renderizar el formulario
        form = SIPOCRowForm()
        form_html = render_to_string('sipoc/add_row_form.html', {'form': form, 'sipoc': sipoc})
        return HttpResponse(form_html)

def add_empty_row(request, sipoc_id):
    sipoc = get_object_or_404(SIPOC, id=sipoc_id)
    # Crear una fila vacía y asociarla con el SIPOC
    row = SIPOCRow.objects.create(sipoc=sipoc)
    # Renderizar solo la fila recién creada para añadir a la tabla
    return render(request, 'sipoc/_row.html', {'row': row})

def edit_row(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    
    if request.method == 'POST':
        form = SIPOCRowForm(request.POST, instance=row)
        if form.is_valid():
            form.save()
            return render(request, 'sipoc/_row.html', {'row': row})  # Renderiza la fila actualizada
        else:
            # Si el formulario es inválido, re-renderiza el formulario con errores
            return render(request, 'sipoc/_row_edit_form.html', {'form': form, 'row': row})
    else:
        # Si es GET, muestra el formulario de edición
        form = SIPOCRowForm(instance=row)
        return render(request, 'sipoc/_row_edit_form.html', {'form': form, 'row': row})


def delete_row(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    row.delete()
    return HttpResponse('')  # Responde con contenido vacío para eliminar la fila

def edit_suppliers(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    if request.method == 'POST':
        form = SIPOCRowSuppliersForm(request.POST, instance=row)
        if form.is_valid():
            form.save()
            return render(request, 'sipoc/_row.html', {'row': row})
    else:
        form = SIPOCRowSuppliersForm(instance=row)
    return render(request, 'sipoc/edits/supplier_edit.html', {'form': form, 'row': row})

def edit_inputs(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    if request.method == 'POST':
        form = SIPOCRowInputsForm(request.POST, instance=row)
        if form.is_valid():
            form.save()
            return render(request, 'sipoc/_row.html', {'row': row})
    else:
        form = SIPOCRowInputsForm(instance=row)
    return render(request, 'sipoc/edits/input_edit.html', {'form': form, 'row': row})

def edit_processes(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    if request.method == 'POST':
        form = SIPOCRowProcessesForm(request.POST, instance=row)
        if form.is_valid():
            form.save()
            return render(request, 'sipoc/_row.html', {'row': row})
    else:
        form = SIPOCRowProcessesForm(instance=row)
    return render(request, 'sipoc/edits/process_edit.html', {'form': form, 'row': row})

def edit_outputs(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    if request.method == 'POST':
        form = SIPOCRowOutputsForm(request.POST, instance=row)
        if form.is_valid():
            form.save()
            return render(request, 'sipoc/_row.html', {'row': row})
    else:
        form = SIPOCRowOutputsForm(instance=row)
    return render(request, 'sipoc/edits/output_edit.html', {'form': form, 'row': row})

def edit_customers(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    if request.method == 'POST':
        form = SIPOCRowCustomersForm(request.POST, instance=row)
        if form.is_valid():
            form.save()
            return render(request, 'sipoc/_row.html', {'row': row})
    else:
        form = SIPOCRowCustomersForm(instance=row)
    return render(request, 'sipoc/edits/customer_edit.html', {'form': form, 'row': row})

def add_supplier(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            row.suppliers.add(supplier)
            # Return the updated row
            return render(request, 'sipoc/_row.html', {'row': row})
    else:
        form = SupplierForm()
    return render(request, 'sipoc/create/add_supplier.html', {'form': form, 'row': row})

def add_input(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            input_instance = form.save()
            row.inputs.add(input_instance)
            # Return the updated row
            return render(request, 'sipoc/_row.html', {'row': row})
    else:
        form = InputForm()
    return render(request, 'sipoc/create/add_input.html', {'form': form, 'row': row})

def add_process(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    if request.method == 'POST':
        form = ProcessForm(request.POST)
        if form.is_valid():
            process = form.save()
            row.processes.add(process)
            # Return the updated row
            return render(request, 'sipoc/_row.html', {'row': row})
    else:
        form = ProcessForm()
    return render(request, 'sipoc/create/add_process.html', {'form': form, 'row': row})

def add_output(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    if request.method == 'POST':
        form = OutputForm(request.POST)
        if form.is_valid():
            output = form.save()
            row.outputs.add(output)
            # Return the updated row
            return render(request, 'sipoc/_row.html', {'row': row})
    else:
        form = OutputForm()
    return render(request, 'sipoc/create/add_output.html', {'form': form, 'row': row})

def add_customer(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            row.customers.add(customer)
            # Return the updated row
            return render(request, 'sipoc/_row.html', {'row': row})
    else:
        form = CustomerForm()
    return render(request, 'sipoc/create/add_customer.html', {'form': form, 'row': row})

def cancel_edit_row(request, row_id):
    row = get_object_or_404(SIPOCRow, id=row_id)
    return render(request, 'sipoc/_row.html', {'row': row})

from django.shortcuts import render, get_object_or_404
from .models import SIPOC, Supplier, Input, Process, Output, Customer, SIPOCRow

def supplier_list(request, sipoc_id):
    sipoc = get_object_or_404(SIPOC, id=sipoc_id)
    suppliers = Supplier.objects.filter(sipoc_rows__sipoc=sipoc).distinct()
    return render(request, 'sipoc/flujograms/supplier_list.html', {'suppliers': suppliers, 'sipoc': sipoc})

def input_list(request, sipoc_id):
    sipoc = get_object_or_404(SIPOC, id=sipoc_id)
    inputs = Input.objects.filter(sipoc_rows__sipoc=sipoc).distinct()
    return render(request, 'sipoc/flujograms/input_list.html', {'inputs': inputs, 'sipoc': sipoc})

def process_list(request, sipoc_id):
    sipoc = get_object_or_404(SIPOC, id=sipoc_id)
    processes = Process.objects.filter(sipoc_rows__sipoc=sipoc).distinct()
    return render(request, 'sipoc/flujograms/process_list.html', {'processes': processes, 'sipoc': sipoc})

def output_list(request, sipoc_id):
    sipoc = get_object_or_404(SIPOC, id=sipoc_id)
    outputs = Output.objects.filter(sipoc_rows__sipoc=sipoc).distinct()
    return render(request, 'sipoc/flujograms/output_list.html', {'outputs': outputs, 'sipoc': sipoc})

def customer_list(request, sipoc_id):
    sipoc = get_object_or_404(SIPOC, id=sipoc_id)
    customers = Customer.objects.filter(sipoc_rows__sipoc=sipoc).distinct()
    return render(request, 'sipoc/flujograms/customer_list.html', {'customers': customers, 'sipoc': sipoc})
