from django.shortcuts import render

# Create your views here.
def contract(request):
    return render(request, 'contract/contract.html')


def opportunity(request):
    return render(request, 'opportunity/opportunity.html')
