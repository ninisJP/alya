from django.db import models

class Candidate(models.Model):
    date = models.DateField(null=True, blank=True)
    department = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    birth_date = models.DateField(null=True, blank=True)
    salary_expectation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    observations = models.TextField(null=True, blank=True)
    availability = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    proposed_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    police_clearance = models.BooleanField(default=False)
    criminal_clearance = models.BooleanField(default=False)
    id_number = models.CharField(max_length=15, null=True, blank=True)
    license_type = models.CharField(max_length=50, null=True, blank=True)
    photo = models.ImageField(upload_to='candidates/photos', null=True, blank=True)
    resume = models.FileField(upload_to='candidates/resumes', null=True, blank=True)

    def __str__(self):
        return self.name
