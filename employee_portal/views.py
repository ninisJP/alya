from django.shortcuts import render
 
def index_portal(request):
    return render(request, 'index_portal.html') 
