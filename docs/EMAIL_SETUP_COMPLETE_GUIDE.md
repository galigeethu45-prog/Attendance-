# Complete Email Setup Guide

## 🎯 Goal
Set up real-time email sending for password reset feature.

---

## 🚀 Quick Start (Choose One)

### Option A: Gmail (Easiest & Most Reliable)

**Time: 5 minutes**

1. **Enable 2FA on Gmail**
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" → "Windows Computer"
   - Click "Generate"
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
   - **Remove all spaces!** → `abcdefghijklmnop`

3. **Update .env file**
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

4. **Restart server & test**
   ```bash
   # Stop server (Ctrl+C)
   python manage.py runserver
   
   # In another terminal
   python test_email_config.py
   ```

---

### Option B: Outlook/Hotmail

**Time: 3 minutes**

1. **Update .env file**
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp-mail.outlook.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@outlook.com
   EMAIL_HOST_PASSWORD=your-password
   DEFAULT_FROM_EMAIL=your-email@outlook.com
   ```

2. **If you have 2FA:**
   - Go to: https://account.microsoft.com/security
   - Create app password
   - Use app password instead of regular password

3. **Restart server & test**

---

### Option C: Office 365 Business (@arraafiinfotech.com)

**Time: 5 minutes**

1. **Update .env file**
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.office365.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@arraafiinfotech.com
   EMAIL_HOST_PASSWORD=your-password
   DEFAULT_FROM_EMAIL=your-email@arraafiinfotech.com
   ```

2. **If port 587 doesn't work, try:**
   - Port 25: `EMAIL_PORT=25`
   - Port 465: `EMAIL_PORT=465` + `EMAIL_USE_SSL=True`

3. **Restart server & test**

---

## 📝 Step-by-Step Instructions

### Step 1: Choose Your Provider

Run the interactive wizard:
```bash
python setup_email_smtp.py
```

This will guide you through the setup.

### Step 2: Edit .env File

1. Open `.env` file in your project root
2. Find the "EMAIL CONFIGURATION" section
3. Uncomment the lines for your chosen provider
4. Fill in your email and password
5. Save the file

### Step 3: Restart Django Server

```bash
# Stop the server (press Ctrl+C in the terminal running Django)
# Start it again
python manage.py runserver
```

### Step 4: Test Email Sending

```bash
python test_email_config.py
```

Enter your email address when prompted and check your inbox!

### Step 5: Test Password Reset

1. Go to: http://127.0.0.1:8000/login/
2. Click "Forgot Password?"
3. Enter your email address
4. Check your email inbox (and spam folder)
5. Click the reset link
6. Set new password
7. Login with new password

---

## ✅ Verification Checklist

- [ ] .env file updated with email settings
- [ ] Django server restarted
- [ ] Test email sent successfully
- [ ] Test email received in inbox
- [ ] Password reset email sent
- [ ] Password reset link works
- [ ] Can login with new password

---

## 🔧 Troubleshooting

### Gmail Issues

**"Username and Password not accepted"**
- ✅ Use App Password, not regular password
- ✅ Remove all spaces from app password
- ✅ Verify 2FA is enabled

**Email goes to spam**
- ✅ Normal for first few emails
- ✅ Mark as "Not Spam"
- ✅ Future emails will go to inbox

### Outlook Issues

**"Connection refused"**
- ✅ Try port 25 or 465
- ✅ Check firewall settings
- ✅ Verify email and password

**"Authentication failed"**
- ✅ Use app password if 2FA enabled
- ✅ Check email spelling
- ✅ Try regular password first

### General Issues

**No email received**
- ✅ Check spam/junk folder
- ✅ Verify email address is correct
- ✅ Check terminal for error messages
- ✅ Run test_email_config.py for details

**"SMTPAuthenticationError"**
- ✅ Wrong username or password
- ✅ For Gmail: Use app password
- ✅ For Outlook: Check 2FA settings

**"Connection timed out"**
- ✅ Check internet connection
- ✅ Try different port
- ✅ Check firewall/antivirus

---

## 📚 Additional Resources

- **Gmail Setup**: See `GMAIL_SMTP_SETUP.md`
- **Outlook Setup**: See `OUTLOOK_SMTP_SETUP.md`
- **Interactive Wizard**: Run `python setup_email_smtp.py`
- **Test Configuration**: Run `python test_email_config.py`

---

## 🔒 Security Best Practices

✅ **DO:**
- Use app passwords when available
- Keep .env file in .gitignore
- Use environment variables in production
- Rotate passwords regularly
- Monitor sent emails

❌ **DON'T:**
- Commit .env file to git
- Share your email password
- Use regular password if app password available
- Use console backend in production
- Hardcode credentials in code

---

## 🎉 Success!

Once configured, your password reset feature will:
- ✅ Send real emails to users
- ✅ Include secure reset links
- ✅ Work in production
- ✅ Be professional and reliable

---

## 💡 Pro Tips

1. **Gmail is most reliable** for development and small deployments
2. **Use company email** (@arraafiinfotech.com) for professional appearance
3. **Test thoroughly** before going to production
4. **Monitor email delivery** in first few days
5. **Consider dedicated email service** (SendGrid, Mailgun) for high volume

---

## 🆘 Need Help?

If you're stuck:
1. Run `python test_email_config.py` to see detailed error
2. Check the specific setup guide for your provider
3. Verify all credentials are correct
4. Try a different email provider
5. Check firewall/antivirus settings

---

**Ready to go? Follow the Quick Start guide above! 🚀**
