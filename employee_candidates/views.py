from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Candidate
from .forms import CandidateForm

def candidate_list(request):
    form = CandidateForm()
    candidates = Candidate.objects.all()
    return render(request, 'candidates/candidate_list.html', {'form': form, 'candidates': candidates})

def add_candidate(request):
    if request.method == "POST":
        form = CandidateForm(request.POST)
        if form.is_valid():
            form.save()
            candidates = Candidate.objects.all()
            return render(request, 'partials/candidate_table.html', {'candidates': candidates})

def edit_candidate(request, id):
    candidate = get_object_or_404(Candidate, id=id)
    if request.method == "POST":
        form = CandidateForm(request.POST, instance=candidate)
        if form.is_valid():
            form.save()
            candidates = Candidate.objects.all()
            return render(request, 'partials/candidate_table.html', {'candidates': candidates})
    else:
        form = CandidateForm(instance=candidate)
        return render(request, 'partials/candidate_form.html', {'form': form, 'candidate': candidate})

def delete_candidate(request, id):
    candidate = get_object_or_404(Candidate, id=id)
    candidate.delete()
    candidates = Candidate.objects.all()
    return render(request, 'partials/candidate_table.html', {'candidates': candidates})
