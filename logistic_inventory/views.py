from django.shortcuts import render

# Create your views here.
def index_logistic(request):
    return render(request, 'index_logistic.html')