# Generated by Django 5.1.1 on 2024-09-17 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistic_inventory', '0014_alter_type_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='type',
            name='category',
            field=models.CharField(choices=[('Equipo', 'Equipo'), ('EPPS', 'Epps'), ('Material', 'Material'), ('Consumible', 'Consumible'), ('Herramienta', 'Herramienta')], default='Equipo', max_length=100),
        ),
    ]