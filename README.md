# AttendanceHub - Employee Attendance Management System

A modern, production-ready Django-based attendance management system with beautiful UI/UX, animations, and complete workflow management.

## Features

### Employee Features
- ✅ Check-in/Check-out with automatic time tracking
- ☕ Break management (Tea & Lunch breaks with limits)
- 📊 Personal dashboard with statistics
- 📅 Attendance history with filters and export
- 🏖️ Leave request management
- 🔔 Real-time notifications
- 👤 Profile management

### HR Features
- 👥 Employee attendance overview
- 📈 Analytics and reports with charts
- ✅ Leave approval/rejection system
- 📊 Department-wise statistics
- 📉 Performance tracking

### Technical Features
- 🎨 Modern, responsive UI with animations
- 🔐 Secure authentication system
- 📱 Mobile-friendly design
- 🚀 Production-ready configuration
- 💾 SQLite database (easily switchable to PostgreSQL)
- 🎯 Clean, maintainable code structure

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup Steps

1. Clone the repository
```bash
git clone <repository-url>
cd attendance-system
```

2. Create and activate virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser
```bash
python manage.py createsuperuser
```

7. Create employee profile for superuser
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from attendance.models import EmployeeProfile

user = User.objects.get(username='your-username')
EmployeeProfile.objects.create(
    user=user,
    department='IT',
    designation='Manager',
    is_hr=True
)
exit()
```

8. Collect static files
```bash
python manage.py collectstatic --noinput
```

9. Run development server
```bash
python manage.py runserver
```

10. Access the application
- Main App: http://localhost:8000/
- Admin Panel: http://localhost:8000/admin/

## Usage

### For Employees
1. Login with your credentials
2. Check-in when you start work
3. Take breaks as needed (within limits)
4. Check-out when you finish
5. View your attendance history
6. Request leaves when needed

### For HR
1. Login with HR credentials
2. Access HR Dashboard from navigation
3. View all employee attendance
4. Approve/reject leave requests
5. Generate reports and analytics

## Configuration

### Break Rules
Edit `attendance/models.py` to modify break rules:
```python
BREAK_RULES = {
    'tea': {
        'max_count': 2,
        'allowed_minutes': 15,
    },
    'lunch': {
        'max_count': 1,
        'allowed_minutes': 45,
    }
}
```

### Work Hours
Modify check-in time validation in `attendance/views.py`:
```python
# Late if after 9:30 AM
if check_in_time.hour > 9 or (check_in_time.hour == 9 and check_in_time.minute > 30):
    attendance.status = 'late'
```

## Production Deployment

### Using Gunicorn
```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables for Production
```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Database Migration to PostgreSQL
1. Install psycopg2: `pip install psycopg2-binary`
2. Update DATABASES in settings.py
3. Run migrations: `python manage.py migrate`

## Project Structure
```
attendance-system/
├── attendance/          # Main app
│   ├── models.py       # Database models
│   ├── views.py        # View functions
│   ├── urls.py         # URL routing
│   └── admin.py        # Admin configuration
├── core/               # Project settings
│   ├── settings.py     # Django settings
│   ├── urls.py         # Root URL config
│   └── wsgi.py         # WSGI config
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── requirements.txt    # Python dependencies
└── manage.py          # Django management script
```

## Technologies Used
- Django 5.0
- Bootstrap 5.3
- Font Awesome 6.4
- Animate.css
- Chart.js
- JavaScript (ES6+)

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License.

## Support
For issues and questions, please create an issue in the repository.

## Author
Developed with ❤️ for modern workforce management
