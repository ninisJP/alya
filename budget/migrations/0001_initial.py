# Generated by Django 5.1.1 on 2024-09-12 15:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('budget_name', models.CharField(default='', max_length=100, verbose_name='Presupuesto')),
                ('budget_days', models.PositiveIntegerField()),
                ('budget_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('budget_final_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('budget_number', models.CharField(blank=True, max_length=10)),
                ('budget_date', models.DateField()),
                ('budget_tax', models.DecimalField(decimal_places=2, default=18.0, max_digits=5)),
                ('budget_deliver', models.CharField(blank=True, max_length=100, null=True)),
                ('budget_service', models.CharField(blank=True, max_length=100, null=True)),
                ('budget_billing', models.CharField(blank=True, max_length=100, null=True)),
                ('budget_warranty', models.CharField(blank=True, max_length=100, null=True)),
                ('budget_expenses', models.DecimalField(decimal_places=2, max_digits=5)),
                ('budget_utilty', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='BudgetItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('quantity', models.PositiveIntegerField()),
                ('measurement', models.CharField(blank=True, default='', max_length=50)),
                ('unit_price', models.FloatField(default=0)),
                ('daily_price', models.FloatField(default=0)),
                ('final_price', models.FloatField(default=0)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='budget.budget')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
    ]
