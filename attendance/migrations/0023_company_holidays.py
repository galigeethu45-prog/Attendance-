# Generated migration for Company Holiday Calendar System

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0022_add_office_ips_to_system_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyHoliday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True, help_text='Holiday date')),
                ('name', models.CharField(help_text='Holiday name (e.g., Republic Day)', max_length=200)),
                ('holiday_type', models.CharField(
                    choices=[
                        ('weekly_off', 'Weekly Off (Sunday)'),
                        ('second_saturday', '2nd Saturday'),
                        ('fourth_saturday', '4th Saturday'),
                        ('national', 'National Holiday'),
                        ('company', 'Company Holiday'),
                        ('optional', 'Optional Holiday')
                    ],
                    default='company',
                    help_text='Type of holiday',
                    max_length=20
                )),
                ('description', models.TextField(blank=True, help_text='Additional details about the holiday', null=True)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this holiday is active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Company Holiday',
                'verbose_name_plural': 'Company Holidays',
                'ordering': ['date'],
            },
        ),
        migrations.AddIndex(
            model_name='companyholiday',
            index=models.Index(fields=['date', 'is_active'], name='holiday_date_active_idx'),
        ),
        migrations.AddIndex(
            model_name='companyholiday',
            index=models.Index(fields=['holiday_type'], name='holiday_type_idx'),
        ),
        migrations.AddConstraint(
            model_name='companyholiday',
            constraint=models.UniqueConstraint(fields=['date', 'name'], name='unique_holiday_date_name'),
        ),
    ]
