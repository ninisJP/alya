# Generated by Django 5.1.1 on 2024-09-12 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistic_inventory', '0010_alter_item_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='unit',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]