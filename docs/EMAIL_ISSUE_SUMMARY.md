# Email Setup Issue - Summary & Solution

## 🔍 What I Found

I ran comprehensive diagnostics on your email configuration and discovered the issue:

### ✅ What's Working
- Email configuration in `.env` is **correct**
- Django settings are **properly configured**
- Email server hostname resolves correctly: `mail.arraafiinfotech.com` → `162.241.85.151`

### ❌ What's NOT Working
- **ALL SMTP ports are BLOCKED** on your network
- Port 465 (SSL): ❌ Blocked
- Port 587 (TLS): ❌ Blocked  
- Port 25: ❌ Blocked

### 🚨 Root Cause
Your **network/firewall is blocking outgoing SMTP connections**. This could be:
1. Windows Firewall blocking Python
2. Antivirus software blocking SMTP
3. ISP/Corporate network blocking email ports
4. Router firewall settings

## ✅ SOLUTION: Use Gmail SMTP

The fastest and most reliable solution is to use **Gmail SMTP** instead of the company email server.

### Why Gmail?
- ✅ Works from any network (no firewall issues)
- ✅ More reliable and widely accessible
- ✅ Easy to set up (5 minutes)
- ✅ Free for development/testing
- ✅ Professional and secure

### Quick Setup (3 Steps)

#### Step 1: Generate Gmail App Password
1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not enabled)
3. Go to: https://myaccount.google.com/apppasswords
4. Select **Mail** and **Windows Computer**
5. Click **Generate**
6. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

#### Step 2: Run Setup Script
```bash
python switch_to_gmail.py
```

This interactive script will:
- Guide you through the setup
- Update your `.env` file automatically
- Backup your current configuration
- Verify the settings

#### Step 3: Restart Server & Test
```bash
# Stop current server (Ctrl+C)
python manage.py runserver

# In another terminal, test email:
python verify_email_setup.py
```

## 📋 Manual Setup (Alternative)

If you prefer to update `.env` manually:

```env
# Gmail SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_SSL=False
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Important**: 
- Use **App Password**, NOT your regular Gmail password
- Remove spaces from App Password (e.g., `abcd efgh ijkl mnop` → `abcdefghijklmnop`)
- Restart Django server after changes

## 🧪 Testing

After setup, test in this order:

### 1. Test Network Connectivity
```bash
python diagnose_email_connection.py
```
Should show: ✅ Port 587 OPEN for smtp.gmail.com

### 2. Test Email Configuration
```bash
python verify_email_setup.py
```
Enter your email to receive test email

### 3. Test Password Reset
1. Go to: http://127.0.0.1:8000/password-reset/
2. Enter email address
3. Check Gmail inbox (and spam folder)
4. Click reset link
5. Set new password

## 🔧 Troubleshooting

### "App Password not working"
- Make sure 2-Step Verification is enabled
- Generate new App Password
- Remove all spaces from password
- Use the password exactly as generated

### "Email not received"
- Check spam/junk folder
- Verify email address is correct
- Check Django terminal for errors
- Make sure server was restarted

### "Still can't connect"
- Check Windows Firewall settings
- Temporarily disable antivirus
- Try from different network (mobile hotspot)
- Run: `python diagnose_email_connection.py`

## 📁 Helpful Scripts

I created these scripts to help you:

| Script | Purpose |
|--------|---------|
| `switch_to_gmail.py` | Interactive Gmail setup (RECOMMENDED) |
| `diagnose_email_connection.py` | Test network connectivity |
| `verify_email_setup.py` | Comprehensive email test |
| `test_email_config.py` | Simple email test |
| `add_user_email.py` | Add email to user accounts |

## 🎯 Recommended Next Steps

1. **Run Gmail setup** (5 minutes):
   ```bash
   python switch_to_gmail.py
   ```

2. **Restart Django server**:
   ```bash
   python manage.py runserver
   ```

3. **Test email sending**:
   ```bash
   python verify_email_setup.py
   ```

4. **Test password reset**:
   - Go to: http://127.0.0.1:8000/password-reset/
   - Enter email and check inbox

## 💡 About Company Email Server

Your company email server (`mail.arraafiinfotech.com`) is configured correctly, but it's not accessible due to network restrictions.

**For Production**: You may want to:
1. Contact IT to allow SMTP connections
2. Use Gmail for now, switch to company email later
3. Configure email server on production server (where network may be different)

**For Development**: Gmail is perfect and recommended.

## ✅ Success Checklist

- [ ] Generated Gmail App Password
- [ ] Ran `python switch_to_gmail.py`
- [ ] Restarted Django server
- [ ] Ran `python verify_email_setup.py` successfully
- [ ] Received test email in Gmail inbox
- [ ] Tested password reset flow
- [ ] Received password reset email
- [ ] Successfully reset password

## 📞 Need Help?

If you encounter any issues:

1. Run diagnostics: `python diagnose_email_connection.py`
2. Check error messages in Django terminal
3. Verify App Password is correct (no spaces)
4. Make sure server was restarted
5. Check spam folder for emails

---

**Ready to fix this?** Run: `python switch_to_gmail.py`
