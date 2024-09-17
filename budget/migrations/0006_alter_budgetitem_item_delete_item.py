# Generated by Django 5.1.1 on 2024-09-17 15:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0005_remove_budgetitem_measurement_budget_budget_expenses'),
        ('logistic_inventory', '0013_alter_type_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budget_items', to='logistic_inventory.item'),
        ),
        migrations.DeleteModel(
            name='Item',
        ),
    ]
