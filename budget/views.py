from django.shortcuts import render
 
def index_budget(request):
    return render(request, 'index_budget.html') 
