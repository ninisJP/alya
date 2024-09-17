# Generated by Django 5.1.1 on 2024-09-13 17:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_number', models.CharField(max_length=20, unique=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('terms', models.TextField()),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='client.client')),
            ],
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('estimated_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('probability', models.DecimalField(decimal_places=2, help_text='Probabilidad de éxito (en %)', max_digits=5)),
                ('status', models.CharField(choices=[('open', 'Open'), ('won', 'Won'), ('lost', 'Lost')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opportunities', to='client.client')),
            ],
        ),
    ]
