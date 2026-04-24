# Email Setup Guide for Password Reset

## Current Status
- ✅ Password reset feature is implemented
- ⚠️ Currently using **console backend** (emails printed to terminal, not sent)
- 🎯 Need to configure SMTP to send real emails

## Option 1: Gmail SMTP (Easiest for Testing)

### Step 1: Enable 2-Factor Authentication on Gmail
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Click "Generate"
4. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Step 3: Update .env File
Add these lines to your `.env` file:

```env
# Email Configuration for Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

Replace:
- `your-email@gmail.com` with your actual Gmail address
- `abcdefghijklmnop` with the app password you generated (remove spaces)

### Step 4: Restart Django Server
```bash
# Stop the server (Ctrl+C)
# Start it again
python manage.py runserver
```

### Step 5: Test
1. Go to login page
2. Click "Forgot Password?"
3. Enter your email
4. Check your inbox (and spam folder)

---

## Option 2: Company Email (arraafiinfotech.com)

If you have SMTP credentials for @arraafiinfotech.com domain:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@arraafiinfotech.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@arraafiinfotech.com
```

Contact your email provider for:
- SMTP host (e.g., smtp.office365.com, smtp.zoho.com)
- Port (usually 587 or 465)
- Username and password

---

## Option 3: Keep Console Backend (Development Only)

If you want to keep testing without real emails:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Emails will be printed in the terminal where you run `python manage.py runserver`.

---

## Testing Email Configuration

Run this test script:

```bash
python test_email_config.py
```

This will:
- Check your email settings
- Send a test email
- Show any errors

---

## Troubleshooting

### Gmail: "Less secure app access"
- Gmail no longer supports this
- You MUST use App Passwords (see Step 2 above)

### Email not received
1. Check spam/junk folder
2. Verify email address is correct
3. Check terminal for error messages
4. Run test script to see detailed errors

### "SMTPAuthenticationError"
- Wrong username or password
- For Gmail: Make sure you're using App Password, not regular password

### "Connection refused"
- Wrong host or port
- Check firewall settings
- Try port 465 with EMAIL_USE_SSL=True instead of EMAIL_USE_TLS

---

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env` file to git (it's in .gitignore)
- Never share your email password or app password
- Use environment variables in production
- Consider using a dedicated email service (SendGrid, Mailgun) for production

---

## Production Recommendations

For production, consider:
1. **SendGrid** - Free tier: 100 emails/day
2. **Mailgun** - Free tier: 5,000 emails/month
3. **AWS SES** - Very cheap, reliable
4. **Dedicated SMTP service** from your hosting provider

These are more reliable than Gmail for production use.
