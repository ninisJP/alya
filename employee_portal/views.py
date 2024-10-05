from django.shortcuts import render
from employee.models import Supervisor
 
def index_portal(request):
    user = Supervisor.objects.filter()
    return render(request, 'index_portal.html') 
