# Generated by Django 5.1.1 on 2024-10-11 17:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounting_order_sales', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('valuation', models.CharField(default='D', max_length=1)),
                ('total_time', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CardTaskOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField()),
                ('state', models.BooleanField(default=False)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='follow_control_card.card')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('verb', models.CharField(default='', max_length=100)),
                ('object', models.CharField(default='', max_length=100)),
                ('measurement', models.CharField(default='minutos', max_length=50)),
                ('task_time', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('cards', models.ManyToManyField(related_name='tasks', through='follow_control_card.CardTaskOrder', to='follow_control_card.card')),
                ('sale_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting_order_sales.salesorder')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='cardtaskorder',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='follow_control_card.task'),
        ),
    ]
