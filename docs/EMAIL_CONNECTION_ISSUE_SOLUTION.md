# Email Connection Issue - Solution Guide

## 🔍 Problem Identified

**DNS Resolution**: ✅ Working (mail.arraafiinfotech.com → 162.241.85.151)  
**Port Connectivity**: ❌ **ALL SMTP PORTS BLOCKED**

- Port 25: Blocked
- Port 465 (SSL): Blocked  
- Port 587 (TLS): Blocked
- Port 2525: Blocked

## 🚨 Root Cause

Your network is blocking outgoing SMTP connections. This could be:

1. **Windows Firewall** - Blocking Python/SMTP traffic
2. **Antivirus Software** - Blocking email connections
3. **ISP/Network Firewall** - Corporate or ISP blocking SMTP
4. **Router/Network Settings** - Blocking outgoing port 465/587

## ✅ Solutions (Try in Order)

### Solution 1: Allow Python Through Windows Firewall

1. Open **Windows Defender Firewall**
2. Click **"Allow an app through firewall"**
3. Click **"Change settings"** (requires admin)
4. Click **"Allow another app"**
5. Browse to: `C:\Users\HP\OneDrive\Desktop\Attendance Website\venv\Scripts\python.exe`
6. Check both **Private** and **Public** networks
7. Click **OK**
8. Restart Django server and test again

### Solution 2: Temporarily Disable Antivirus

1. Temporarily disable antivirus software
2. Run: `python diagnose_email_connection.py`
3. If it works, add Python to antivirus exceptions
4. Re-enable antivirus

### Solution 3: Use Gmail SMTP (Recommended Alternative)

Gmail SMTP is more reliable and widely accessible:

#### Step 1: Enable 2-Step Verification
1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification**

#### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select **"Mail"** and **"Windows Computer"**
3. Click **Generate**
4. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

#### Step 3: Update .env File
```env
# Gmail SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_SSL=False
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

#### Step 4: Restart Server
```bash
# Stop current server (Ctrl+C)
python manage.py runserver
```

#### Step 5: Test
```bash
python verify_email_setup.py
```

### Solution 4: Use Outlook/Office 365 SMTP

If you have Office 365 account:

#### Step 1: Update .env File
```env
# Outlook SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_SSL=False
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=your-email@outlook.com
```

**Note**: Your organization has disabled SMTP AUTH for Office 365, so this may not work.

### Solution 5: Try Different Network

1. Connect to **mobile hotspot** (bypass network restrictions)
2. Run: `python diagnose_email_connection.py`
3. If it works, the issue is your network/ISP blocking SMTP

### Solution 6: Contact Email Server Administrator

If company email server must be used:

1. Contact IT/Email administrator
2. Ask them to verify:
   - SMTP server hostname: `mail.arraafiinfotech.com`
   - Accessible ports: 465, 587, or 25
   - Firewall rules allowing your IP
   - Account credentials are correct
3. Ask if there's a different SMTP server for applications

## 🧪 Testing Commands

### Test Network Connectivity
```bash
python diagnose_email_connection.py
```

### Test Email Configuration
```bash
python verify_email_setup.py
```

### Test Sending Email
```bash
python test_email_config.py
```

## 📝 Quick Test with Gmail

Want to test immediately? Use this quick setup:

1. **Get Gmail App Password** (see Step 2 above)

2. **Update .env** (just these lines):
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_SSL=False
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-gmail@gmail.com
```

3. **Restart server**:
```bash
python manage.py runserver
```

4. **Test password reset**:
   - Go to: http://127.0.0.1:8000/password-reset/
   - Enter email address
   - Check Gmail inbox

## ✅ Verification Checklist

After applying solution:

- [ ] Run `python diagnose_email_connection.py` - should show open ports
- [ ] Run `python verify_email_setup.py` - should send test email
- [ ] Django server restarted after .env changes
- [ ] Test password reset at http://127.0.0.1:8000/password-reset/
- [ ] Email received in inbox (check spam folder)
- [ ] Reset link works and can change password

## 🎯 Recommended Solution

**For immediate testing**: Use **Gmail SMTP** (Solution 3)
- Most reliable
- Works from any network
- Easy to set up
- Free for development

**For production**: Contact IT to fix company email server access
- More professional (uses company domain)
- Better for production environment
- May require network/firewall changes

## 📞 Need Help?

1. Run diagnostics: `python diagnose_email_connection.py`
2. Check which ports are accessible
3. Try Gmail SMTP first (easiest solution)
4. If still not working, check Windows Firewall
5. Contact IT if company email must be used

## 🔗 Related Files

- `diagnose_email_connection.py` - Network diagnostics
- `verify_email_setup.py` - Email configuration test
- `test_email_config.py` - Simple email test
- `GMAIL_SMTP_SETUP.md` - Detailed Gmail setup
- `EMAIL_SETUP_COMPLETE_GUIDE.md` - Complete guide
- `.env` - Email configuration file
