# Project Structure Guide

## Clean, Professional Organization

The project has been reorganized into a clean, professional structure.

---

## Folder Structure

```
attendance-system/
├── attendance/              # Backend - Main Django App
│   ├── api/                # API endpoints
│   ├── management/         # Management commands
│   ├── migrations/         # Database migrations
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # URL routing
│   └── admin.py           # Admin configuration
│
├── core/                   # Backend - Project Settings
│   ├── settings.py        # Django settings
│   ├── urls.py            # Root URL configuration
│   └── wsgi.py            # WSGI configuration
│
├── templates/              # Frontend - HTML Templates
│   ├── base.html          # Base template
│   ├── dashboard.html     # Employee dashboard
│   ├── hr_dashboard.html  # HR dashboard
│   ├── login.html         # Login page
│   └── ...                # Other templates
│
├── static/                 # Frontend - Static Assets
│   ├── css/               # Stylesheets
│   │   └── style.css
│   ├── js/                # JavaScript
│   │   └── main.js
│   └── images/            # Images
│
├── docs/                   # Documentation
│   ├── QUICKSTART.md      # Quick start guide
│   ├── FEATURES.md        # Feature documentation
│   ├── DEPLOYMENT.md      # Deployment guide
│   └── ...                # Other documentation
│
├── scripts/                # Utility Scripts
│   ├── setup/             # Setup scripts
│   │   ├── setup_admin_hr.py
│   │   ├── setup_auto_checkout_task.bat
│   │   └── ...
│   ├── test/              # Test scripts
│   │   ├── test_break_system.py
│   │   ├── comprehensive_system_check.py
│   │   └── ...
│   └── maintenance/       # Maintenance scripts
│       ├── fix_old_checkouts.py
│       ├── run_auto_checkout_now.py
│       └── ...
│
├── media/                  # User uploaded files
├── staticfiles/           # Collected static files (production)
├── venv/                  # Virtual environment
│
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # Project README
```

---

## Quick Reference

### Backend (Django)
- **Main App**: `attendance/`
- **Settings**: `core/`
- **Database**: Models in `attendance/models.py`
- **Views**: Logic in `attendance/views.py`
- **URLs**: Routing in `attendance/urls.py`

### Frontend
- **Templates**: `templates/` - HTML files
- **Styles**: `static/css/` - CSS files
- **Scripts**: `static/js/` - JavaScript files
- **Images**: `static/images/` - Image files

### Documentation
- **All Docs**: `docs/` folder
- **Quick Start**: `docs/QUICKSTART.md`
- **Features**: `docs/FEATURES.md`
- **Deployment**: `docs/DEPLOYMENT.md`

### Scripts
- **Setup**: `scripts/setup/` - Initial setup scripts
- **Test**: `scripts/test/` - Testing and verification
- **Maintenance**: `scripts/maintenance/` - Fixes and updates

---

## Common Tasks

### Setup
```bash
# Create admin user
python scripts/setup/setup_admin_hr.py

# Setup auto-checkout
scripts/setup/setup_auto_checkout_no_admin.bat
```

### Testing
```bash
# Test system
python scripts/test/comprehensive_system_check.py

# Test auto-checkout
scripts/test/test_auto_checkout.bat
```

### Maintenance
```bash
# Fix old checkouts
python scripts/maintenance/fix_old_checkouts.py

# Run auto-checkout now
python scripts/maintenance/run_auto_checkout_now.py
```

---

## File Locations

### Configuration
- Environment: `.env`
- Settings: `core/settings.py`
- URLs: `core/urls.py`

### Database
- Models: `attendance/models.py`
- Migrations: `attendance/migrations/`
- SQLite: `db.sqlite3` (development)

### Templates
- Base: `templates/base.html`
- Dashboard: `templates/dashboard.html`
- HR: `templates/hr_dashboard.html`

### Static Files
- CSS: `static/css/style.css`
- JS: `static/js/main.js`

---

## What Was Removed

### Deleted Files (Redundant/Old)
- Old .txt documentation files
- Duplicate setup guides
- Temporary fix scripts
- Unused test files

### Moved Files
- Documentation → `docs/`
- Setup scripts → `scripts/setup/`
- Test scripts → `scripts/test/`
- Maintenance → `scripts/maintenance/`

---

## Benefits of New Structure

### Clean Root Directory
- Only essential files in root
- Easy to navigate
- Professional appearance

### Organized Scripts
- Setup scripts in one place
- Test scripts grouped together
- Maintenance scripts separate

### Clear Documentation
- All docs in `docs/` folder
- Easy to find information
- No clutter in root

### Logical Separation
- Backend: `attendance/`, `core/`
- Frontend: `templates/`, `static/`
- Scripts: `scripts/`
- Docs: `docs/`

---

## Migration Notes

### If You Have Bookmarks/Shortcuts

**Old Location** → **New Location**

Setup Scripts:
- `setup_admin_hr.py` → `scripts/setup/setup_admin_hr.py`
- `setup_auto_checkout_task.bat` → `scripts/setup/setup_auto_checkout_task.bat`

Test Scripts:
- `test_break_system.py` → `scripts/test/test_break_system.py`
- `comprehensive_system_check.py` → `scripts/test/comprehensive_system_check.py`

Documentation:
- `QUICKSTART.md` → `docs/QUICKSTART.md`
- `FEATURES.md` → `docs/FEATURES.md`

---

## Summary

The project is now organized into a clean, professional structure with:
- Clear separation of concerns
- Logical folder hierarchy
- Easy navigation
- Professional appearance
- Better maintainability

All functionality remains the same - only the organization has changed!
