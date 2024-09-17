# Generated by Django 5.1.1 on 2024-09-16 15:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255, verbose_name='Descripción')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio Unitario')),
                ('daily_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio Diario')),
                ('lifespan', models.PositiveIntegerField(verbose_name='Tiempo de Vida (días)')),
                ('item_class', models.CharField(choices=[('herramienta', 'Herramienta'), ('material', 'Material'), ('consumible', 'Consumible')], max_length=50, verbose_name='Clase de Ítem')),
            ],
        ),
        migrations.RemoveField(
            model_name='budget',
            name='budget_billing',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='budget_deliver',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='budget_expenses',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='budget_number',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='budget_service',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='budget_tax',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='budget_utilty',
        ),
        migrations.RemoveField(
            model_name='budget',
            name='budget_warranty',
        ),
        migrations.RemoveField(
            model_name='budgetitem',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='budgetitem',
            name='daily_price',
        ),
        migrations.RemoveField(
            model_name='budgetitem',
            name='object_id',
        ),
        migrations.RemoveField(
            model_name='budgetitem',
            name='unit_price',
        ),
        migrations.AddField(
            model_name='budgetitem',
            name='item',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='budget_items', to='budget.item'),
            preserve_default=False,
        ),
    ]