from django.shortcuts import render

# Create your views here.

from decimal import Decimal
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic.list import ListView
from django.views.decorators.http import require_http_methods, require_POST
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.db.models import Count, Q
from .forms import (
    EditarFechaPagoForm,
    EditarMontoForm,
    CambiarPDFPagoForm,
    PDFUploadForm,
    PagoForm,
    CronogramaForm,
)
from .models import DetallePago, PagoCronograma, Resolucion, Pago
from .models import Cronograma
from django.utils import timezone
import pdfplumber
import re
from datetime import date, datetime, timedelta
from datetime import date, timedelta
from .forms import ReciboSunatForm
from django.db.models import Sum


def crear_cronograma(request):
    if request.method == "POST":
        # Modifica esta línea para incluir request.FILES
        form = CronogramaForm(request.POST, request.FILES)
        if form.is_valid():
            cronograma = form.save()  # Guarda el cronograma y obtén el objeto creado
            return redirect("ver_pagos_cronograma", cronograma_id=cronograma.id)
    else:
        form = CronogramaForm()
    return render(request, "crear_cronograma.html", {"form": form})


def ver_pagos_cronograma(request, cronograma_id):
    cronograma = get_object_or_404(Cronograma, pk=cronograma_id)
    pagos = PagoCronograma.objects.filter(cronograma=cronograma)
    return render(
        request, "ver_pagos_cronograma.html", {"cronograma": cronograma, "pagos": pagos}
    )


def pagos_cronograma(request, cronograma_id):
    pagos = PagoCronograma.objects.filter(cronograma_id=cronograma_id)
    cronograma = get_object_or_404(Cronograma, pk=cronograma_id)
    detalle_cronograma = cronograma.detalle
    return render(
        request,
        "pagos_cronograma.html",
        {"pagos": pagos, "detalle_cronograma": detalle_cronograma},
    )


def ver_cronogramas(request):
    cronogramas = Cronograma.objects.all()
    return render(request, "ver_cronogramas.html", {"cronogramas": cronogramas})

def ver_cronogramas_filtrados(request, tipo):
    if tipo == "sunat":
        cronogramas = Cronograma.objects.filter(entidad__icontains="SUNAT")
    else:
        cronogramas = Cronograma.objects.exclude(entidad__icontains="SUNAT")

    return render(request, "ver_cronogramas.html", {"cronogramas": cronogramas})


# metodos HTMX
@require_http_methods(["POST"])
def editar_monto_pago(request, pago_id):
    if request.method == "POST":
        pago = get_object_or_404(PagoCronograma, id=pago_id)
        nuevo_monto = request.POST.get("monto_pago")
        if nuevo_monto:
            try:
                pago.monto_pago = nuevo_monto
                pago.save()
                return HttpResponse(
                    f"<span>{pago.monto_pago}</span>"
                )  # Respuesta para htmx
            except Exception as e:
                # Manejar la excepción si es necesario
                pass
    # Redireccionar o responder de otra manera si no es una solicitud POST o si hay un error

@require_http_methods(["POST"])
def cambiar_pdf_pago(request, pago_id):
    pago = get_object_or_404(PagoCronograma, pk=pago_id)
    form = CambiarPDFPagoForm(request.POST, request.FILES, instance=pago)
    if form.is_valid():
        form.save()
        # Asume que tienes el ID del cronograma disponible o puedes obtenerlo de `pago`
        cronograma_id = pago.cronograma.id
        return redirect(reverse("pagos_cronograma", args=[cronograma_id]))
    else:
        return JsonResponse({"error": "Datos del formulario no válidos"}, status=400)

def editar_fecha_pago(request, pago_id):
    pago = get_object_or_404(PagoCronograma, pk=pago_id)
    if request.method == "POST":
        form = EditarFechaPagoForm(request.POST, instance=pago)
        if form.is_valid():
            form.save()
            # Redireccionar a donde sea apropiado después de la actualización
            return HttpResponse(
                f"<span>{pago.fecha_pago}</span>"
            )  # Respuesta para htmx
    else:
        form = EditarFechaPagoForm(instance=pago)

    return render(request, "editar_fecha_pago.html", {"form": form, "pago": pago})






# METODO CON PDF PARA SUNAT aqui abajo se veran cosas tenebrosas :O
def cargar_pdf(request):
    if request.method == "POST":
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo_pdf = request.FILES["archivo_pdf"]
            texto_completo = ""
            with pdfplumber.open(archivo_pdf) as pdf:
                for pagina in pdf.pages:
                    texto_completo += pagina.extract_text()

            # Extracción de datos del PDF
            # (La lógica de extracción de datos aquí sigue siendo la misma)
            # Extracción de datos del PDF
            regex_resolucion = r"RESOLUCIÓN DE INTENDENCIA N.° (\d+)"
            regex_aplazamiento = r"(Aplazamiento con Fraccionamiento|Fraccionamiento|Aplazamiento) por (\d+) mes\(es\)"
            regex_tabla = r"([A-Z]+|\d+)\s(\d{2}\/\d{2}\/\d{4})\s([\d,\.]+)\s([\d,\.]+)\s([\d,\.]+)\s([\d,\.]+)"

            numero_resolucion = re.search(regex_resolucion, texto_completo)
            if numero_resolucion:
                numero_resolucion = numero_resolucion.group(1)
            else:
                numero_resolucion = "No encontrado"

            match_aplazamiento = re.search(regex_aplazamiento, texto_completo)
            if match_aplazamiento:
                tipo_resolucion = match_aplazamiento.group(1)
                tiempo_aplazamiento = match_aplazamiento.group(2)
            else:
                tipo_resolucion = "No especificado"
                tiempo_aplazamiento = "No encontrado"

            # Nueva lógica para extraer descripción, monto del tributo, interés y total
            patron = r"(\d{6})\s+(\d{4})\s+(.+?)\s+(\d{3}\d{3}\d{7}\d{4})\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)"
            coincidencias = re.findall(patron, texto_completo, re.DOTALL)
            if coincidencias:
                # Asumiendo que solo quieres la última coincidencia para llenar los campos de la resolución
                descripcion, monto_tributo, interes, total = coincidencias[-1]
                # Ajustar la descripción
                descripcion = " ".join(
                    descripcion.split()[:-1]
                )  # Remueve el número de documento al final, si es necesario
            else:
                # Valores predeterminados en caso de que no se encuentren coincidencias
                descripcion = "Descripción no encontrada"
                monto_tributo = "0"  # Asigna un valor de cadena en lugar de entero
                interes = "0"  # Asigna un valor de cadena
                total = "0"  # Asigna un valor de cadena

            coincidencias_tabla = re.findall(regex_tabla, texto_completo)
            datos_tabla = [
                {
                    "numero_cuota": fila[0],
                    "Vencimiento": fila[1],
                    "Amortización": fila[2],
                    "Interés": fila[3],
                    "Total": fila[4],
                    "Saldo": fila[5],
                }
                for fila in coincidencias_tabla
            ]

            # Guardar los datos de la resolución en la base de datos
            resolucion_obj = Resolucion(
                numero_resolucion=(
                    numero_resolucion if numero_resolucion != "No encontrado" else None
                ),
                tipo_resolucion=tipo_resolucion,
                tiempo_aplazamiento=tiempo_aplazamiento,
                descripcion=descripcion,  # Nuevo campo
                monto_tributo=Decimal(monto_tributo.replace(",", "")),
                interes=Decimal(interes.replace(",", "")),
                total=Decimal(total.replace(",", "")),
                archivo_pdf=archivo_pdf,
            )
            resolucion_obj.save()

            # Guardar los datos de la tabla de pagos
            for fila in datos_tabla:
                Pago.objects.create(
                    resolucion=resolucion_obj,
                    numero_cuota=fila["numero_cuota"],
                    vencimiento=datetime.strptime(
                        fila["Vencimiento"], "%d/%m/%Y"
                    ).date(),
                    amortizacion=Decimal(fila["Amortización"].replace(",", "")),
                    interes=Decimal(fila["Interés"].replace(",", "")),
                    total=Decimal(fila["Total"].replace(",", "")),
                    saldo=Decimal(fila["Saldo"].replace(",", "")),
                )

            # Redirigir al usuario a una página de confirmación o de resumen después del guardado
            return redirect(
                "lista_resoluciones"
            )  # Asegúrate de reemplazar 'url_a_confirmacion' con la URL real

    else:
        form = PDFUploadForm()
    return render(request, "cargar_pdf.html", {"form": form})


# vistas de cronogramas sunat
# * combinar esta otra vista
class ResolucionListView(ListView):
    model = Resolucion
    context_object_name = "resoluciones"
    template_name = "resolucion_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resoluciones'] = Resolucion.objects.annotate(
            num_pagos=Count('pagos'),
            num_pagos_pagados=Count('pagos', filter=Q(pagos__pagado=True))
        )
        return context


@require_POST  # Asegura que esta vista solo pueda ser accedida mediante un método POST
def eliminar_resolucion(request, pk):
    resolucion = get_object_or_404(Resolucion, pk=pk)
    resolucion.delete()
    messages.success(request, "Resolución eliminada con éxito.")
    return redirect(reverse("lista_resoluciones"))

def detalle_resolucion(request, pk):
    resolucion = get_object_or_404(Resolucion, pk=pk)
    pagos = Pago.objects.filter(resolucion=resolucion)

    # No necesitas manejar el método POST ni el formulario en esta vista
    return render(
        request,
        "detalle_resolucion.html",
        {
            "resolucion": resolucion,
            "pagos": pagos,
        },
    )

def cambiar_pdf_pago_sunat(request, pk):
    if request.method == "POST":
        pago = get_object_or_404(Pago, pk=pk)
        # Verifica si se está editando el monto_pagado_sunat
        if 'monto_pagado_sunat' in request.POST:
            monto_pagado = request.POST['monto_pagado_sunat']
            # Realiza las validaciones necesarias
            # Por ejemplo, asegúrate de que el monto_pagado sea un valor válido
            # Luego actualiza el campo monto_pagado_sunat y guarda el objeto
            pago.monto_pagado_sunat = monto_pagado
            pago.save()
            return JsonResponse({'message': 'Monto pagado actualizado correctamente'})
        # Verifica si se está cambiando el archivo PDF
        elif 'pago_sunat' in request.FILES:
            form = PagoForm(request.POST, request.FILES, instance=pago)
            if form.is_valid():
                form.save()
                # Retorna algo adecuado para htmx, por ejemplo, un enlace al nuevo PDF
                return HttpResponse(
                    f'<a href="{pago.pago_sunat.url}" target="_blank">Ver Documento</a>'
                )
    # Manejar caso de error o solicitud no POST
    return HttpResponse("Operación no permitida", status=405)


#### CRONOGRAMA SEMAFORO
# * combinar esta vista
def cronograma_semaforo(request):
    if request.method == 'POST':
        form = ReciboSunatForm(request.POST, request.FILES)
        pago_id = request.POST.get('pago_id')

        # Usamos get_object_or_404 para manejar adecuadamente si el pago no existe
        try:
            pago = get_object_or_404(Pago, id=pago_id)
        except ValueError:
            # Captura el error si pago_id no es válido (por ejemplo, no es un entero)
            form.add_error(None, 'ID de pago no válido.')
            pago = None

        if form.is_valid() and pago is not None:
            recibo = form.save(commit=False)
            recibo.pago = pago
            recibo.save()
            recibo.pago.update_monto_pagado_sunat()  # Actualizar el monto pagado después de guardar el recibo
            messages.success(request, 'El recibo ha sido registrado exitosamente.')
            return redirect('cronograma_semaforo')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ReciboSunatForm()

    hoy = date.today()
    proximo = hoy + timedelta(days=30)
    ahora = timezone.localtime(timezone.now())

    # Filtrar pagos que no están completamente saldados
    pagos = Pago.objects.filter(vencimiento__gte=date.today(), pagado=False).order_by('vencimiento')

    for pago in pagos:
        if pago.vencimiento < hoy:
            pago.estado_clase = 'table-danger'
        elif pago.vencimiento <= proximo:
            pago.estado_clase = 'table-warning'
        else:
            pago.estado_clase = 'table-success'

    return render(request, 'semaforo.html', {
        'pagos': pagos,
        'ahora': ahora,
        'form': form  # Agregar el formulario y los mensajes al contexto
    })


# ! Prueba
class ResolucionPagoListView(ListView):
    model = Resolucion
    context_object_name = "resoluciones"
    template_name = "combined_template.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['resoluciones'] = Resolucion.objects.annotate(
            num_pagos=Count('pagos'),
            num_pagos_pagados=Count('pagos', filter=Q(pagos__pagado=True))
        )

        hoy = date.today()
        proximo = hoy + timedelta(days=30)

        # Asegurarse de que las sumas y cálculos sean con respecto al campo 'total'
        resoluciones_con_datos = Resolucion.objects.annotate(
            num_pagos=Count('pagos'),
            num_pagos_pagados=Count('pagos', filter=Q(pagos__pagado=True)),
            total_deuda=Sum('pagos__total'),  # Usa 'total' para calcular la deuda
            total_pagado=Sum('pagos__monto_pagado_sunat', filter=Q(pagos__pagado=True))
        )

        for resolucion in resoluciones_con_datos:
            resolucion.saldo_restante = resolucion.total_deuda - resolucion.total_pagado if resolucion.total_deuda and resolucion.total_pagado else 0

        pagos = Pago.objects.filter(pagado=False).order_by('vencimiento')
        for pago in pagos:
            if pago.vencimiento < hoy:
                pago.estado_clase = 'table-danger'
            elif pago.vencimiento <= proximo:
                pago.estado_clase = 'table-warning'
            else:
                pago.estado_clase = 'table-success'

        context['resoluciones'] = resoluciones_con_datos
        context['pagos'] = pagos
        context['ahora'] = timezone.localtime(timezone.now())
        context['form'] = ReciboSunatForm()  # Asumimos que este formulario se inicializa aquí
        return context


    def post(self, request, *args, **kwargs):
        form = ReciboSunatForm(request.POST, request.FILES)
        print("Form data:", request.POST)  # Debugging: ver los datos del formulario
        if form.is_valid():
            print("Form is valid")  # Debugging
            recibo = form.save(commit=False)
            pago_id = request.POST.get('pago_id')
            recibo.pago = Pago.objects.get(id=pago_id)
            recibo.save()
            recibo.pago.update_monto_pagado_sunat()
            return redirect('combined_view')
        else:
            print("Form is not valid", form.errors)  # Debugging: ver errores del formulario
        return self.get(request, *args, **kwargs)

    model = Resolucion
    context_object_name = "resoluciones"
    template_name = "combined_template.html"



