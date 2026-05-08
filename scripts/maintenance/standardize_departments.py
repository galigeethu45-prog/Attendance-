"""
Standardize department names in the database
Fixes inconsistencies like "Information Technology" → "IT"
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from attendance.models import EmployeeProfile, EmployeeMasterData

def standardize_departments():
    """
    Standardize department names across the system
    """
    print("=" * 60)
    print("DEPARTMENT STANDARDIZATION SCRIPT")
    print("=" * 60)
    
    # Department mapping (old_name → new_name)
    department_mapping = {
        'Information Technology': 'IT',
        'information technology': 'IT',
        'Information technology': 'IT',
        'INFORMATION TECHNOLOGY': 'IT',
        'Human Resources': 'HR',
        'human resources': 'HR',
        'HUMAN RESOURCES': 'HR',
    }
    
    # Update EmployeeProfile
    print("\n1. Updating EmployeeProfile...")
    profile_count = 0
    for old_name, new_name in department_mapping.items():
        profiles = EmployeeProfile.objects.filter(department=old_name)
        count = profiles.count()
        if count > 0:
            profiles.update(department=new_name)
            profile_count += count
            print(f"   ✓ Updated {count} profiles: '{old_name}' → '{new_name}'")
    
    if profile_count == 0:
        print("   ✓ No profiles needed updating")
    else:
        print(f"   ✓ Total profiles updated: {profile_count}")
    
    # Update EmployeeMasterData
    print("\n2. Updating EmployeeMasterData...")
    master_count = 0
    for old_name, new_name in department_mapping.items():
        master_data = EmployeeMasterData.objects.filter(department=old_name)
        count = master_data.count()
        if count > 0:
            master_data.update(department=new_name)
            master_count += count
            print(f"   ✓ Updated {count} master records: '{old_name}' → '{new_name}'")
    
    if master_count == 0:
        print("   ✓ No master data needed updating")
    else:
        print(f"   ✓ Total master records updated: {master_count}")
    
    # Show current department distribution
    print("\n3. Current Department Distribution:")
    print("   EmployeeProfile:")
    profiles_by_dept = EmployeeProfile.objects.values('department').distinct()
    for dept in profiles_by_dept:
        if dept['department']:
            count = EmployeeProfile.objects.filter(department=dept['department']).count()
            print(f"      - {dept['department']}: {count} employees")
    
    print("\n   EmployeeMasterData:")
    master_by_dept = EmployeeMasterData.objects.values('department').distinct()
    for dept in master_by_dept:
        if dept['department']:
            count = EmployeeMasterData.objects.filter(department=dept['department']).count()
            print(f"      - {dept['department']}: {count} records")
    
    print("\n" + "=" * 60)
    print("✅ DEPARTMENT STANDARDIZATION COMPLETE!")
    print("=" * 60)
    print("\nRecommendation: Add department dropdown in forms to prevent")
    print("future inconsistencies. Standard departments: IT, HR, Finance,")
    print("Operations, Sales, Marketing, etc.")
    print("=" * 60)

if __name__ == '__main__':
    try:
        standardize_departments()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
