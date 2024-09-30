# Generated by Django 5.1.1 on 2024-09-26 02:01

import django.db.models.deletion
import follow_control_technician.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounting_order_sales', '0001_initial'),
        ('employee', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TechnicianTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verb', models.CharField(max_length=50)),
                ('object', models.CharField(max_length=100)),
                ('measurement', models.CharField(max_length=50)),
                ('time', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='TechnicianCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('technician', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employee.technician')),
            ],
        ),
        migrations.CreateModel(
            name='TechnicianCardTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('total_time', models.DecimalField(decimal_places=2, editable=False, max_digits=7)),
                ('order', models.PositiveIntegerField()),
                ('photo', models.ImageField(blank=True, null=True, upload_to=follow_control_technician.models.rename_file)),
                ('status', models.BooleanField(default=False)),
                ('saler_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_order_sales.salesorder')),
                ('technician_card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='follow_control_technician.techniciancard')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='follow_control_technician.techniciantask')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
