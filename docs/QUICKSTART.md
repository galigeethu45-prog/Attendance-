# 🚀 Quick Start Guide - AttendanceHub

Get your attendance system up and running in 5 minutes!

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)

## Installation Steps

### Step 1: Navigate to Project Directory
```bash
cd "C:\Users\HP\OneDrive\Desktop\Attendance Website"
```

### Step 2: Activate Virtual Environment
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies (if not already done)
```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations (if not already done)
```bash
python manage.py migrate
```

### Step 5: Create Demo Users (if not already done)
```bash
python setup.py
```

### Step 6: Start Development Server
```bash
python manage.py runserver
```

### Step 7: Access the Application
Open your browser and go to: **http://localhost:8000/**

You will see the login page. Use the credentials below to login.

## 🎉 You're Ready!

### Login Credentials

**HR Admin Account:**
- Username: `hr_admin`
- Password: `admin123`
- Access: Full system access + HR dashboard

**Employee Account 1:**
- Username: `employee1`
- Password: `emp123`
- Access: Employee dashboard

**Employee Account 2:**
- Username: `employee2`
- Password: `emp123`
- Access: Employee dashboard

## 📱 Quick Tour

### For Employees:

1. **Login** with employee credentials
2. **Check In** - Click the "Check In" button on dashboard
3. **Take a Break** - Click "Tea" or "Lunch" break button
4. **End Break** - Click "End Break" when done
5. **Check Out** - Click "Check Out" at end of day
6. **View History** - Navigate to "History" to see your attendance records
7. **Request Leave** - Go to "Leave" section to submit leave requests

### For HR:

1. **Login** with HR credentials
2. **View Dashboard** - See all employee attendance at a glance
3. **HR Panel** - Click "HR Panel" in navigation
4. **Approve Leaves** - Go to "Leave Requests" tab
5. **View Reports** - Check "Reports" tab for analytics

## 🎨 Features to Try

### Employee Features:
- ✅ Check-in/Check-out tracking
- ✅ Break management (Tea: 2x15min, Lunch: 1x45min)
- ✅ View attendance history with filters
- ✅ Request different types of leaves
- ✅ View notifications
- ✅ Update profile

### HR Features:
- ✅ Monitor all employee attendance
- ✅ Approve/reject leave requests
- ✅ View analytics and charts
- ✅ Department-wise statistics
- ✅ Export reports

## 🔧 Common Tasks

### Create a New Employee
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from attendance.models import EmployeeProfile

user = User.objects.create_user(
    username='newemployee',
    email='new@example.com',
    password='password123',
    first_name='New',
    last_name='Employee'
)

EmployeeProfile.objects.create(
    user=user,
    department='IT',
    designation='Developer',
    is_hr=False
)
```

### Access Django Admin
1. Go to: http://localhost:8000/admin/
2. Login with superuser credentials (create one if needed):
```bash
python manage.py createsuperuser
```

### Reset Database (Start Fresh)
```bash
# Delete database
del db.sqlite3

# Delete migrations (except __init__.py)
# Then run:
python manage.py makemigrations
python manage.py migrate
python setup.py
```

## 📊 Test Scenarios

### Scenario 1: Normal Day
1. Login as employee1
2. Check in at 9:00 AM
3. Take tea break at 11:00 AM (15 min)
4. Take lunch break at 1:00 PM (45 min)
5. Take another tea break at 4:00 PM (15 min)
6. Check out at 6:00 PM
7. View your attendance history

### Scenario 2: Late Arrival
1. Login as employee2
2. Check in at 10:00 AM (after 9:30 AM)
3. Notice "Late" status
4. Complete the day normally

### Scenario 3: Leave Request
1. Login as employee1
2. Go to "Leave" section
3. Submit a leave request for next week
4. Logout
5. Login as hr_admin
6. Go to HR Panel → Leave Requests
7. Approve the leave request
8. Logout and login as employee1
9. Check notifications for approval

### Scenario 4: Break Limit
1. Login as employee1
2. Check in
3. Take 2 tea breaks (allowed)
4. Try to take a 3rd tea break (should be blocked)
5. Check notifications for limit warning

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Use different port
python manage.py runserver 8080
```

### Static files not loading
```bash
python manage.py collectstatic --clear --noinput
```

### Database errors
```bash
# Reset migrations
python manage.py migrate --run-syncdb
```

### Module not found errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Next Steps

1. **Customize Break Rules**: Edit `attendance/models.py` → `BREAK_RULES`
2. **Change Work Hours**: Edit `attendance/views.py` → `check_in` function
3. **Add More Employees**: Use Django admin or shell
4. **Configure Email**: Update `core/settings.py` with SMTP settings
5. **Deploy to Production**: Follow `DEPLOYMENT.md`

## 🎯 Tips

- Use Chrome/Firefox for best experience
- Keep the terminal open while server is running
- Press `Ctrl+C` to stop the server
- Check console for any errors
- Use Django admin for quick data management

## 📞 Need Help?

- Check `README.md` for detailed documentation
- Review `FEATURES.md` for complete feature list
- See `DEPLOYMENT.md` for production setup
- Check Django logs in terminal

## 🎊 Enjoy AttendanceHub!

Your modern attendance management system is ready to use. Start tracking attendance with style! 🚀
