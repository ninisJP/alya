from django.shortcuts import render
from django.http import HttpResponse


def hub(request):
    return render(request, 'hub.html')
