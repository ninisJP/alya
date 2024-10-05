# Generated by Django 5.1.1 on 2024-09-30 03:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Suppliers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.CharField(blank=True, default='', max_length=20, null=True, unique=True, verbose_name='RUC/DNI')),
                ('name', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Nombre del Proveedor')),
                ('bank', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Nombre del Banco')),
                ('account', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Número de Cuenta')),
                ('currency', models.CharField(blank=True, choices=[('Soles', 'Soles'), ('Dólares', 'Dólares')], default='Soles', max_length=20, null=True, verbose_name='Moneda')),
                ('interbank_currency', models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Cuenta Interbancaria')),
            ],
            options={
                'verbose_name': 'Proveedor',
                'verbose_name_plural': 'Proveedores',
            },
        ),
    ]