# Generated by Django 5.1.1 on 2024-09-16 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_item_remove_budget_budget_billing_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetitem',
            name='final_price',
            field=models.FloatField(blank=True, default=0),
        ),
    ]
