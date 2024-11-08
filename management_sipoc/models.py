from django.db import models

class Supplier(models.Model):
    """Modelo para Proveedor (S)"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Input(models.Model):
    """Modelo para Entrada (I)"""
    content = models.CharField(max_length=255)

    def __str__(self):
        return self.content


class Process(models.Model):
    """Modelo para Proceso (P)"""
    step = models.CharField(max_length=255)

    def __str__(self):
        return self.step


class Output(models.Model):
    """Modelo para Salida (O)"""
    result = models.CharField(max_length=255)

    def __str__(self):
        return self.result


class Customer(models.Model):
    """Modelo para Cliente (C)"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class SIPOC(models.Model):
    """Modelo principal de SIPOC que agrupa filas de S, I, P, O, C"""
    name = models.CharField(max_length=100)  # Nombre o descripción del SIPOC
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SIPOCRow(models.Model):
    """Modelo para una fila de S, I, P, O, C en un SIPOC"""
    sipoc = models.ForeignKey(SIPOC, on_delete=models.CASCADE, related_name='rows')
    suppliers = models.ManyToManyField(Supplier, related_name='sipoc_rows')
    inputs = models.ManyToManyField(Input, related_name='sipoc_rows')
    processes = models.ManyToManyField(Process, related_name='sipoc_rows')
    outputs = models.ManyToManyField(Output, related_name='sipoc_rows')
    customers = models.ManyToManyField(Customer, related_name='sipoc_rows')

    def __str__(self):
        return f"Fila SIPOC - {self.sipoc.name}"
