# Generated by Django 5.1.1 on 2024-09-12 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logistic_inventory', '0003_type_alter_product_type_delete_producttype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subtype',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
