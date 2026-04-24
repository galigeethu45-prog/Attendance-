# Email Setup Verification Guide

## Current Configuration

Your email is configured with:
- **Email Server**: mail.arraafiinfotech.com
- **Port**: 465 (SSL)
- **From Email**: giri.g@arraafiinfotech.com
- **Backend**: SMTP (real email sending)

## Quick Verification Steps

### Step 1: Verify Configuration
Run the verification script to check all settings:
```bash
python verify_email_setup.py
```

This will:
- ✅ Check all email settings
- ✅ Test network connectivity to email server
- ✅ Send a test email (if you provide an email address)
- ✅ Show any configuration errors

### Step 2: Restart Django Server
**IMPORTANT**: After changing .env file, you MUST restart the server:

1. Stop the current server (Ctrl+C in terminal)
2. Start it again:
```bash
python manage.py runserver
```

### Step 3: Test Password Reset
1. Go to: http://127.0.0.1:8000/password-reset/
2. Enter an email address (e.g., giri.g@arraafiinfotech.com)
3. Click "Send Reset Link"
4. Check email inbox (and spam folder)
5. Click the reset link in email
6. Set new password

## Troubleshooting

### If Email Not Received

**Check 1: Server Running?**
- Make sure Django server was restarted after .env changes
- Old server instance won't have new email settings

**Check 2: Correct Email Address?**
- Verify the email address exists in the system
- Check user has email set: `python manage.py shell`
  ```python
  from django.contrib.auth.models import User
  User.objects.filter(email__isnull=False).values('username', 'email')
  ```

**Check 3: Email Server Credentials?**
- Verify password is correct: `Gali123$5`
- Check if email account is active
- Try logging into webmail with same credentials

**Check 4: Spam Folder?**
- Check spam/junk folder in email inbox
- Add noreply@arraafiinfotech.com to contacts

**Check 5: Server Logs?**
- Check Django terminal for error messages
- Look for authentication or connection errors

### Common Errors

**Error: "Authentication failed"**
- Wrong username or password
- Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env

**Error: "Connection refused"**
- Email server not accessible
- Check firewall settings
- Verify EMAIL_HOST and EMAIL_PORT

**Error: "SSL/TLS error"**
- Wrong security settings for port
- Port 465 needs: EMAIL_USE_SSL=True, EMAIL_USE_TLS=False
- Port 587 needs: EMAIL_USE_TLS=True, EMAIL_USE_SSL=False

## Alternative: Gmail SMTP

If company email server doesn't work, you can use Gmail:

1. Enable 2-Step Verification in Google Account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Update .env:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_SSL=False
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```
4. Restart Django server

## Verification Checklist

- [ ] .env file has correct email settings
- [ ] Django server restarted after .env changes
- [ ] verify_email_setup.py runs without errors
- [ ] Test email received in inbox
- [ ] Password reset email received
- [ ] Password reset link works
- [ ] Can login with new password

## Need Help?

1. Run: `python verify_email_setup.py` - shows detailed diagnostics
2. Check Django terminal for error messages
3. Verify email credentials by logging into webmail
4. Try Gmail SMTP as alternative (see above)

## Files to Check

- `.env` - Email configuration
- `core/settings.py` - Django email settings
- `verify_email_setup.py` - Verification script
- `test_email_config.py` - Simple test script
