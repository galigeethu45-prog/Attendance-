# Generated migration for multi-date selection, manager role, and onsite requests

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attendance', '0020_systemsettings'),
    ]

    operations = [
        # Add Manager role to EmployeeProfile.role choices
        migrations.AlterField(
            model_name='employeeprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('employee', 'Employee'),
                    ('team_leader', 'Team Leader'),
                    ('manager', 'Manager'),
                    ('hr', 'HR/Admin')
                ],
                db_index=True,
                default='employee',
                max_length=20
            ),
        ),
        
        # Add multi-date selection and hierarchical approval to LeaveRequest
        migrations.AddField(
            model_name='leaverequest',
            name='selected_dates',
            field=models.JSONField(blank=True, help_text='List of specific dates (for non-consecutive leaves)', null=True),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='tl_comment',
            field=models.TextField(blank=True, help_text="Team Leader's comment", null=True),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='tl_approved',
            field=models.BooleanField(default=False, help_text='Team Leader approval status'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='tl_approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tl_approved_leaves', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='tl_approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='manager_comment',
            field=models.TextField(blank=True, help_text="Manager's comment", null=True),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='manager_approved',
            field=models.BooleanField(default=False, help_text='Manager approval status'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='manager_approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manager_approved_leaves', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='manager_approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        
        # Add multi-date selection and hierarchical approval to WFHRequest
        migrations.AddField(
            model_name='wfhrequest',
            name='selected_dates',
            field=models.JSONField(blank=True, help_text='List of specific dates (for non-consecutive WFH)', null=True),
        ),
        migrations.AddField(
            model_name='wfhrequest',
            name='tl_comment',
            field=models.TextField(blank=True, help_text="Team Leader's comment", null=True),
        ),
        migrations.AddField(
            model_name='wfhrequest',
            name='tl_approved',
            field=models.BooleanField(default=False, help_text='Team Leader approval status'),
        ),
        migrations.AddField(
            model_name='wfhrequest',
            name='tl_approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tl_approved_wfh', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='wfhrequest',
            name='tl_approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='wfhrequest',
            name='manager_comment',
            field=models.TextField(blank=True, help_text="Manager's comment", null=True),
        ),
        migrations.AddField(
            model_name='wfhrequest',
            name='manager_approved',
            field=models.BooleanField(default=False, help_text='Manager approval status'),
        ),
        migrations.AddField(
            model_name='wfhrequest',
            name='manager_approver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manager_approved_wfh', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='wfhrequest',
            name='manager_approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        
        # Create OnsiteRequest model
        migrations.CreateModel(
            name='OnsiteRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visit_type', models.CharField(choices=[('onsite', 'Onsite Visit (Physical)'), ('online_meeting', 'Online Client Meeting (From Office)')], default='onsite', max_length=20)),
                ('visit_date', models.DateField()),
                ('client_name', models.CharField(help_text='Client/Project name', max_length=200)),
                ('location', models.TextField(help_text="Client location or 'Online' for virtual meetings")),
                ('purpose', models.TextField(help_text='Purpose of visit/meeting')),
                ('expected_duration', models.CharField(help_text="e.g., '2 hours', '10 AM - 4 PM'", max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('hr_comment', models.TextField(blank=True, null=True)),
                ('manager_comment', models.TextField(blank=True, null=True)),
                ('manager_approved', models.BooleanField(default=False)),
                ('manager_approved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('actual_check_in', models.DateTimeField(blank=True, help_text='When employee checked in for onsite visit', null=True)),
                ('actual_check_out', models.DateTimeField(blank=True, help_text='When employee checked out from onsite visit', null=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('hr_approver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_onsite_requests', to=settings.AUTH_USER_MODEL)),
                ('manager_approver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manager_approved_onsite', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-visit_date'],
            },
        ),
        migrations.AddIndex(
            model_name='onsiterequest',
            index=models.Index(fields=['employee', 'visit_date'], name='attendance_o_employe_idx'),
        ),
        migrations.AddIndex(
            model_name='onsiterequest',
            index=models.Index(fields=['status', 'visit_date'], name='attendance_o_status_idx'),
        ),
    ]
