# Generated migration for adding office IP management

from django.db import migrations, models


def create_default_office_ips(apps, schema_editor):
    """
    Initialize with current hardcoded IP
    """
    SystemSettings = apps.get_model('attendance', 'SystemSettings')
    settings, created = SystemSettings.objects.get_or_create(pk=1)
    
    # Set default office IPs with the current one (as Python list, not JSON string)
    settings.office_ips = [
        {
            'ip': '14.195.138.241',
            'description': 'Main Office (Regus)',
            'added_at': '2026-05-06T12:00:00Z',
            'added_by': 'System Migration',
            'is_active': True
        }
    ]
    settings.save()


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0021_add_multidate_manager_onsite'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemsettings',
            name='office_ips',
            field=models.JSONField(
                default=list,
                help_text='List of allowed office IP addresses with metadata',
                blank=True
            ),
        ),
        migrations.RunPython(create_default_office_ips, reverse_code=migrations.RunPython.noop),
    ]
