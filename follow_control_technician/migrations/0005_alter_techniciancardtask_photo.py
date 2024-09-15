import follow_control_technician.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('follow_control_technician', '0004_techniciancardtask_photo_techniciancardtask_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='techniciancardtask',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=follow_control_technician.models.rename_file),
        ),
    ]