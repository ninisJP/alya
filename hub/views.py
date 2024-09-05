from django.shortcuts import render

def hub(request):
    return render(request, 'hub.html')
