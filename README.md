# AttendanceHub - Employee Attendance Management System

A comprehensive Django-based attendance management system with automatic checkout, break tracking, leave management, and HR dashboard.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python manage.py migrate
```

### 3. Create Admin User
```bash
python scripts/setup/setup_admin_hr.py
```

### 4. Run Server
```bash
python manage.py runserver
```

### 5. Setup Auto-Checkout (Optional)
```bash
# Windows
scripts/setup/setup_auto_checkout_no_admin.bat

# Linux
scripts/setup/setup_auto_checkout.sh
```

## Documentation

- **Quick Start**: `docs/QUICKSTART.md`
- **Features**: `docs/FEATURES.md`
- **Deployment**: `docs/DEPLOYMENT.md`
- **Full Docs**: `docs/` folder

## Project Structure

```
attendance-system/
├── attendance/          # Main Django app (backend)
├── core/               # Project settings (backend)
├── templates/          # HTML templates (frontend)
├── static/            # CSS, JS, images (frontend)
├── docs/              # Documentation
├── scripts/           # Utility scripts
│   ├── setup/        # Setup scripts
│   ├── test/         # Test scripts
│   └── maintenance/  # Maintenance scripts
├── manage.py          # Django management
└── requirements.txt   # Dependencies
```

## Features

- Automatic check-in/check-out
- Break management (Tea & Lunch)
- Leave request system
- HR dashboard with analytics
- Work mode (Office/Hybrid/WFH)
- Emergency override for network issues
- Auto-checkout at 7 PM
- Audit logging
- Master data management

## Configuration

1. Copy `.env.example` to `.env`
2. Update database settings
3. Update email settings (optional)
4. Set your office IP address in `attendance/views.py`

## Support

For detailed documentation, see `docs/` folder.

## License

MIT License
