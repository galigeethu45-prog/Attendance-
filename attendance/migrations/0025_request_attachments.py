from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import attendance.models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0024_remove_companyholiday_unique_holiday_date_name_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_type', models.CharField(choices=[('leave', 'Leave Request'), ('wfh', 'WFH Request'), ('onsite', 'Onsite Request'), ('overtime', 'Overtime Request')], max_length=20)),
                ('request_id', models.IntegerField(help_text='ID of the related request')),
                ('file', models.FileField(upload_to=attendance.models.attachment_upload_path)),
                ('original_filename', models.CharField(max_length=255)),
                ('file_size', models.PositiveIntegerField(default=0, help_text='File size in bytes')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_attachments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['uploaded_at'],
            },
        ),
    ]
