from django.shortcuts import render

# Create your views here.
def hub(request):
    return render(request, 'hub.html')
