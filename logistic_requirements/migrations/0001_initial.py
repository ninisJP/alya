# Generated by Django 5.1.1 on 2024-09-20 21:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounting_order_sales', '0003_alter_salesorder_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequirementOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requested_date', models.DateField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sales_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_order_sales.salesorder')),
            ],
        ),
        migrations.CreateModel(
            name='RequirementOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_requested', models.PositiveIntegerField(default=1)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
                ('requirement_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='logistic_requirements.requirementorder')),
                ('sales_order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_order_sales.salesorderitem')),
            ],
        ),
    ]
