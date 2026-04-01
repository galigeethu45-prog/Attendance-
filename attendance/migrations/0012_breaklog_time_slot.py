# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0011_alter_leaverequest_leave_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='breaklog',
            name='time_slot',
            field=models.CharField(
                choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')],
                default='morning',
                max_length=10,
                null=True,
                blank=True
            ),
        ),
    ]
