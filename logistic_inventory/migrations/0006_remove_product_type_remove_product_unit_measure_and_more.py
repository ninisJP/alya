# Generated by Django 5.1.1 on 2024-09-12 17:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistic_inventory', '0005_subtype_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='type',
        ),
        migrations.RemoveField(
            model_name='product',
            name='unit_measure',
        ),
        migrations.AddField(
            model_name='product',
            name='subtype',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='logistic_inventory.subtype'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='logistic_inventory.brand'),
        ),
        migrations.AlterField(
            model_name='type',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
