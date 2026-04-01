# Generated for Employee Master Data system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attendance', '0012_breaklog_time_slot'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeMasterData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(db_index=True, max_length=20, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('date_of_birth', models.DateField()),
                ('blood_group', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=5)),
                ('department', models.CharField(max_length=100)),
                ('designation', models.CharField(max_length=100)),
                ('date_of_joining', models.DateField()),
                ('phone_number', models.CharField(max_length=15)),
                ('alternate_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('local_address', models.TextField()),
                ('permanent_address', models.TextField()),
                ('aadhar_number', models.CharField(max_length=12)),
                ('pan_number', models.CharField(max_length=10)),
                ('account_created', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_master_data', to=settings.AUTH_USER_MODEL)),
                ('linked_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='master_data', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Employee Master Data',
                'verbose_name_plural': 'Employee Master Data',
                'ordering': ['employee_id'],
            },
        ),
        migrations.AddIndex(
            model_name='employeemasterdata',
            index=models.Index(fields=['employee_id', 'email', 'date_of_birth'], name='attendance_e_employe_idx'),
        ),
    ]
