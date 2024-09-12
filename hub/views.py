from django.shortcuts import render
from django.http import HttpResponse
from django_htmx.http import HttpResponseLocation


def hub(request):
    if request.htmx:
        return HttpResponseLocation("/presupuestos/")
    else:
        return render(request, 'hub.html')
