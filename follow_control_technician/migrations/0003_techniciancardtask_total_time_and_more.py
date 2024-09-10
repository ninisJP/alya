# Generated by Django 5.1.1 on 2024-09-09 03:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting_order_sales', '0003_alter_salesorder_project'),
        ('follow_control_technician', '0002_alter_techniciancard_technician_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='techniciancardtask',
            name='total_time',
            field=models.DecimalField(decimal_places=2, default=20, editable=False, max_digits=7),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='techniciancardtask',
            name='saler_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_order_sales.salesorder'),
        ),
    ]