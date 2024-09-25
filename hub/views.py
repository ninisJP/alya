from django.shortcuts import render
from django.http import HttpResponse
from django_htmx.http import HttpResponseLocation, HttpResponseClientRedirect


def hub(request):
    if request.htmx:
        destiny = request.GET.get('destiny')
        if destiny == 'presupuestos':
            return HttpResponseClientRedirect('/presupuestos/')
        elif destiny == 'proyectos':
            return HttpResponseClientRedirect('/proyectos/')
        elif destiny == 'clientes':
            return HttpResponseClientRedirect('/clientes/')
        elif destiny == 'tarjeta-control':
            return HttpResponseClientRedirect('/tarjeta-control/')
        else:
            return HttpResponseClientRedirect('/default/')
    else:
        return render(request, 'hub.html')

