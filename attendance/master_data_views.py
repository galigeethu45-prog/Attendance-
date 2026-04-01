"""
Master Data Management Views
Handles HR operations for employee master data
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from .models import EmployeeMasterData, AuditLog
from django.contrib.auth.models import User
import csv
import io
from datetime import datetime

# Helper function to check if user is HR
def is_hr_or_admin(user):
    if user.is_superuser:
        return True
    try:
        return user.employeeprofile.is_hr
    except:
        return False

# =========================
# MASTER DATA LIST VIEW
# =========================
@login_required
@user_passes_test(is_hr_or_admin)
def master_data_list(request):
    """View all employee master data"""
    master_data = EmployeeMasterData.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        master_data = master_data.filter(
            employee_id__icontains=search
        ) | master_data.filter(
            first_name__icontains=search
        ) | master_data.filter(
            last_name__icontains=search
        ) | master_data.filter(
            email__icontains=search
        )
    
    context = {
        'master_data_list': master_data,
        'total_count': EmployeeMasterData.objects.count(),
        'registered_count': EmployeeMasterData.objects.filter(account_created=True).count(),
    }
    
    return render(request, 'master_data_list.html', context)


# =========================
# ADD MASTER DATA (MANUAL)
# =========================
@login_required
@user_passes_test(is_hr_or_admin)
def add_master_data(request):
    """Manually add single employee master data"""
    if request.method == 'POST':
        try:
            # Parse date fields
            dob = datetime.strptime(request.POST.get('date_of_birth'), '%Y-%m-%d').date()
            doj = datetime.strptime(request.POST.get('date_of_joining'), '%Y-%m-%d').date()
            
            # Create master data
            master_data = EmployeeMasterData.objects.create(
                employee_id=request.POST.get('employee_id').strip(),
                first_name=request.POST.get('first_name').strip(),
                middle_name=request.POST.get('middle_name', '').strip() or None,
                last_name=request.POST.get('last_name').strip(),
                gender=request.POST.get('gender'),
                date_of_birth=dob,
                blood_group=request.POST.get('blood_group'),
                department=request.POST.get('department').strip(),
                designation=request.POST.get('designation').strip(),
                date_of_joining=doj,
                phone_number=request.POST.get('phone_number').strip(),
                alternate_phone=request.POST.get('alternate_phone', '').strip() or None,
                email=request.POST.get('email').strip().lower(),
                local_address=request.POST.get('local_address').strip(),
                permanent_address=request.POST.get('permanent_address').strip(),
                aadhar_number=request.POST.get('aadhar_number').strip(),
                pan_number=request.POST.get('pan_number').strip().upper(),
                created_by=request.user
            )
            
            # Log action
            AuditLog.objects.create(
                user=request.user,
                action='master_data_create',
                description=f'Added master data for {master_data.employee_id} - {master_data.get_full_name()}'
            )
            
            messages.success(request, f'Master data added successfully for {master_data.get_full_name()}!')
            return redirect('master_data_list')
            
        except Exception as e:
            messages.error(request, f'Error adding master data: {str(e)}')
    
    return render(request, 'add_master_data.html')


# =========================
# BULK UPLOAD CSV
# =========================
@login_required
@user_passes_test(is_hr_or_admin)
def bulk_upload_master_data(request):
    """Bulk upload employee master data via CSV"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        try:
            csv_file = request.FILES['csv_file']
            
            # Read CSV
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            success_count = 0
            error_count = 0
            errors = []
            
            with transaction.atomic():
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Parse dates
                        dob = datetime.strptime(row['Date of Birth'].strip(), '%d-%b-%Y').date()
                        doj = datetime.strptime(row['Joining Date'].strip(), '%d-%b-%Y').date()
                        
                        # Create or update
                        master_data, created = EmployeeMasterData.objects.update_or_create(
                            employee_id=row['ID Number'].strip(),
                            defaults={
                                'first_name': row['First Name'].strip(),
                                'middle_name': row.get('Middle Name', '').strip() or None,
                                'last_name': row['Last Name'].strip(),
                                'gender': row['Gender'].strip().lower(),
                                'date_of_birth': dob,
                                'blood_group': row['Blood Group'].strip(),
                                'department': row['Department'].strip(),
                                'designation': row['Designation'].strip(),
                                'date_of_joining': doj,
                                'phone_number': row['Phone No'].strip(),
                                'alternate_phone': row.get('Alternate Phone No', '').strip() or None,
                                'email': row['Email'].strip().lower(),
                                'local_address': row['Local Address'].strip(),
                                'permanent_address': row['Permanent Address'].strip(),
                                'aadhar_number': row['Aadhaar Card No'].strip(),
                                'pan_number': row['PAN Number'].strip().upper(),
                                'created_by': request.user
                            }
                        )
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {row_num}: {str(e)}")
            
            # Log action
            AuditLog.objects.create(
                user=request.user,
                action='master_data_bulk_upload',
                description=f'Bulk uploaded {success_count} records, {error_count} errors'
            )
            
            if error_count == 0:
                messages.success(request, f'Successfully uploaded {success_count} employee records!')
            else:
                messages.warning(request, f'Uploaded {success_count} records with {error_count} errors. Check details below.')
                for error in errors[:10]:  # Show first 10 errors
                    messages.error(request, error)
            
            return redirect('master_data_list')
            
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
    
    return render(request, 'bulk_upload_master_data.html')


# =========================
# EDIT MASTER DATA
# =========================
@login_required
@user_passes_test(is_hr_or_admin)
def edit_master_data(request, master_id):
    """Edit employee master data"""
    master_data = get_object_or_404(EmployeeMasterData, id=master_id)
    
    if request.method == 'POST':
        try:
            # Parse dates
            dob = datetime.strptime(request.POST.get('date_of_birth'), '%Y-%m-%d').date()
            doj = datetime.strptime(request.POST.get('date_of_joining'), '%Y-%m-%d').date()
            
            # Update fields
            master_data.first_name = request.POST.get('first_name').strip()
            master_data.middle_name = request.POST.get('middle_name', '').strip() or None
            master_data.last_name = request.POST.get('last_name').strip()
            master_data.gender = request.POST.get('gender')
            master_data.date_of_birth = dob
            master_data.blood_group = request.POST.get('blood_group')
            master_data.department = request.POST.get('department').strip()
            master_data.designation = request.POST.get('designation').strip()
            master_data.date_of_joining = doj
            master_data.phone_number = request.POST.get('phone_number').strip()
            master_data.alternate_phone = request.POST.get('alternate_phone', '').strip() or None
            master_data.email = request.POST.get('email').strip().lower()
            master_data.local_address = request.POST.get('local_address').strip()
            master_data.permanent_address = request.POST.get('permanent_address').strip()
            master_data.aadhar_number = request.POST.get('aadhar_number').strip()
            master_data.pan_number = request.POST.get('pan_number').strip().upper()
            master_data.save()
            
            # Update linked user profile if exists
            if master_data.linked_user:
                profile = master_data.linked_user.employeeprofile
                profile.date_of_birth = dob
                profile.blood_group = master_data.blood_group
                profile.phone_number = master_data.phone_number
                profile.alternate_phone = master_data.alternate_phone or ''
                profile.local_address = master_data.local_address
                profile.permanent_address = master_data.permanent_address
                profile.aadhar_number = master_data.aadhar_number
                profile.pan_number = master_data.pan_number
                profile.department = master_data.department
                profile.designation = master_data.designation
                profile.date_of_joining = doj
                profile.save()
            
            # Log action
            AuditLog.objects.create(
                user=request.user,
                action='master_data_update',
                description=f'Updated master data for {master_data.employee_id} - {master_data.get_full_name()}'
            )
            
            messages.success(request, 'Master data updated successfully!')
            return redirect('master_data_list')
            
        except Exception as e:
            messages.error(request, f'Error updating master data: {str(e)}')
    
    context = {'master_data': master_data}
    return render(request, 'edit_master_data.html', context)


# =========================
# DELETE MASTER DATA
# =========================
@login_required
@user_passes_test(is_hr_or_admin)
def delete_master_data(request, master_id):
    """Delete employee master data"""
    if request.method == 'POST':
        master_data = get_object_or_404(EmployeeMasterData, id=master_id)
        
        if master_data.account_created:
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete master data for employees who have created accounts'
            })
        
        employee_id = master_data.employee_id
        name = master_data.get_full_name()
        master_data.delete()
        
        # Log action
        AuditLog.objects.create(
            user=request.user,
            action='master_data_delete',
            description=f'Deleted master data for {employee_id} - {name}'
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})


# =========================
# RESET PASSWORD
# =========================
@login_required
@user_passes_test(is_hr_or_admin)
def reset_employee_password(request, user_id):
    """HR resets employee password"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        new_password = request.POST.get('new_password')
        
        if not new_password or len(new_password) < 6:
            return JsonResponse({
                'success': False,
                'message': 'Password must be at least 6 characters'
            })
        
        user.set_password(new_password)
        user.save()
        
        # Log action
        AuditLog.objects.create(
            user=request.user,
            action='password_reset',
            description=f'Reset password for {user.username}',
            target_user=user
        )
        
        messages.success(request, f'Password reset successfully for {user.username}')
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
