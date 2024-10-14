# Generated by Django 5.1.1 on 2024-10-11 17:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounting_order_sales', '0001_initial'),
        ('logistic_suppliers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RequirementOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_date', models.DateField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order_number', models.CharField(blank=True, max_length=20, unique=True)),
                ('estado', models.BooleanField(default=False)),
                ('total_order', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('purchase_order_created', models.BooleanField(default=False)),
                ('sales_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requirement_orders', to='accounting_order_sales.salesorder')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RequirementOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sap_code', models.CharField(default='', max_length=50)),
                ('quantity_requested', models.PositiveIntegerField(default=1)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
                ('estado', models.CharField(choices=[('L', 'Listo'), ('P', 'Pendiente'), ('C', 'Comprando')], default='P', max_length=1)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('requirement_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='logistic_requirements.requirementorder')),
                ('sales_order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_order_sales.salesorderitem')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='logistic_suppliers.suppliers')),
            ],
        ),
    ]
