# Generated by Django 5.1.1 on 2024-09-09 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('follow_control_technician', '0003_techniciancardtask_total_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='techniciancardtask',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='technician_tasks_photos/'),
        ),
        migrations.AddField(
            model_name='techniciancardtask',
            name='status',
            field=models.CharField(choices=[('not_done', 'No Hecha'), ('incomplete', 'Incompleta'), ('completed', 'Completada')], default='not_done', max_length=12),
        ),
    ]
