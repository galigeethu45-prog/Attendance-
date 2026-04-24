# Gmail SMTP Setup Guide

## Prerequisites
- Gmail account
- 2-Factor Authentication enabled

## Step 1: Enable 2-Factor Authentication

1. Go to: https://myaccount.google.com/security
2. Scroll to "Signing in to Google"
3. Click "2-Step Verification"
4. Follow the setup process
5. ✅ Verify it's enabled

## Step 2: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
2. You might need to sign in again
3. Select app: **Mail**
4. Select device: **Windows Computer** (or Other)
5. Click **Generate**
6. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
7. ⚠️ **IMPORTANT**: Remove all spaces when copying!

## Step 3: Update .env File

Add these lines to your `.env` file:

```env
# Gmail SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Replace:**
- `your-email@gmail.com` → Your actual Gmail address
- `abcdefghijklmnop` → The app password (no spaces!)

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

Enter your email when prompted and check your inbox!

## Troubleshooting

### "Username and Password not accepted"
- Make sure you're using **App Password**, not your regular Gmail password
- Remove all spaces from the app password
- Verify 2FA is enabled

### "SMTPAuthenticationError"
- Double-check the app password
- Try generating a new app password
- Make sure EMAIL_HOST_USER matches the Gmail account

### Email goes to Spam
- This is normal for first few emails
- Mark as "Not Spam"
- Future emails should go to inbox

## Security Notes

✅ App passwords are safer than regular passwords
✅ You can revoke app passwords anytime
✅ Never share your app password
✅ Never commit .env file to git
