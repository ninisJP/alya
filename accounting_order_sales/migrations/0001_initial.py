# Generated by Django 5.1.1 on 2024-10-05 03:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('logistic_suppliers', '0001_initial'),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sapcode', models.PositiveBigIntegerField(default=0)),
                ('detail', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.project')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('requested_date', models.DateField(blank=True, null=True)),
                ('requested_by', models.CharField(blank=True, max_length=20, null=True, verbose_name='Encargado')),
                ('acepted', models.BooleanField(default=True)),
                ('salesorder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase_orders', to='accounting_order_sales.salesorder')),
            ],
        ),
        migrations.CreateModel(
            name='SalesOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sap_code', models.CharField(default='', max_length=50)),
                ('description', models.CharField(default='', max_length=50)),
                ('amount', models.IntegerField(default=0, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('price_total', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('unit_of_measurement', models.CharField(default='UND', max_length=10)),
                ('remaining_requirement', models.IntegerField(blank=True, null=True)),
                ('salesorder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='accounting_order_sales.salesorder')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sap_code', models.CharField(default='', max_length=50)),
                ('class_pay', models.CharField(default='', max_length=50)),
                ('type_pay', models.CharField(default='', max_length=50)),
                ('quantity_requested', models.PositiveIntegerField(default=1)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('price_total', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('mov_number', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('bank', models.CharField(blank=True, max_length=100, null=True)),
                ('purchaseorder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='accounting_order_sales.purchaseorder')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='logistic_suppliers.suppliers')),
                ('sales_order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_order_sales.salesorderitem')),
            ],
        ),
    ]
