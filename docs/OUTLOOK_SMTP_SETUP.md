# Outlook/Office 365 SMTP Setup Guide

## For Personal Outlook.com Accounts

### Step 1: Enable SMTP in Outlook

1. Go to: https://outlook.live.com/mail/options/mail/accounts
2. Click "Forwarding and POP/IMAP"
3. Make sure IMAP is enabled

### Step 2: Update .env File

```env
# Outlook SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-outlook-password
DEFAULT_FROM_EMAIL=your-email@outlook.com
```

**Replace:**
- `your-email@outlook.com` → Your Outlook email
- `your-outlook-password` → Your Outlook password

### Step 3: If You Have 2FA Enabled

If you have 2-Factor Authentication:

1. Go to: https://account.microsoft.com/security
2. Click "Advanced security options"
3. Under "App passwords", click "Create a new app password"
4. Copy the generated password
5. Use this password in EMAIL_HOST_PASSWORD

---

## For Office 365 Business Accounts

If you have @arraafiinfotech.com or other business domain:

### Step 1: Get SMTP Settings from IT Admin

Ask your IT admin for:
- SMTP server address
- Port number
- Authentication requirements

### Step 2: Common Office 365 Business Settings

```env
# Office 365 Business SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@arraafiinfotech.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=your-email@arraafiinfotech.com
```

### Step 3: Alternative Port (if 587 doesn't work)

Try port 25:

```env
EMAIL_PORT=25
EMAIL_USE_TLS=True
```

Or port 465 with SSL:

```env
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
```

---

## Step 4: Restart Django Server

```bash
# Stop the server (Ctrl+C)
# Start again
python manage.py runserver
```

## Step 5: Test

```bash
python test_email_config.py
```

---

## Troubleshooting

### "Connection refused"
- Try different ports: 587, 25, or 465
- Check if your network/firewall blocks SMTP
- Contact IT admin if using business account

### "Authentication failed"
- Verify email and password are correct
- If 2FA enabled, use app password
- For business accounts, check with IT admin

### "Relay access denied"
- Your account might not have SMTP permissions
- Contact IT admin for business accounts
- Try using personal Outlook account instead

### Emails not received
- Check spam/junk folder
- Verify recipient email is correct
- Check Outlook sent items to confirm email was sent

---

## Which to Use?

### Use Gmail if:
✅ You have a Gmail account
✅ You want reliable delivery
✅ You're okay with "via gmail.com" in email headers

### Use Outlook if:
✅ You have Outlook/Office 365 account
✅ You want to use company domain (@arraafiinfotech.com)
✅ Your company uses Office 365

### Use Company SMTP if:
✅ You have dedicated SMTP server
✅ You want professional appearance
✅ You need high volume sending

---

## Security Notes

⚠️ **IMPORTANT:**
- Never share your email password
- Use app passwords when available
- Never commit .env file to git
- Rotate passwords regularly
- Monitor sent emails for suspicious activity
