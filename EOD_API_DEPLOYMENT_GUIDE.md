# EOD API - PRODUCTION DEPLOYMENT GUIDE

**Status:** ✅ Ready for Deployment  
**Date:** October 5, 2026

---

## 🎯 QUICK START

Your EOD API is ready to deploy. Follow these steps:

---

## 1️⃣ GENERATE PRODUCTION API KEY

On your **production server**, run:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output:**
```
X7k9mN2pQ4vR8tY6wZ3bA5cD1eF0gH7jL9mK
```

**⚠️ IMPORTANT:**
- Save this key securely
- Never commit to Git
- Never share via email or unsecured channels
- Generate a NEW key for production (don't use test key)

---

## 2️⃣ UPDATE PRODUCTION .env FILE

On your **production server**, edit `.env`:

```bash
nano /path/to/smartpunch/.env
```

Add this line:

```bash
# EOD API Integration
EOD_API_KEY=X7k9mN2pQ4vR8tY6wZ3bA5cD1eF0gH7jL9mK
```

Replace with your actual key from Step 1.

Save and exit.

---

## 3️⃣ DEPLOY THE CODE

### Option A: Git Pull (Recommended)

```bash
cd /path/to/smartpunch
git pull origin main
```

### Option B: Manual Copy

Copy these files to production:
- `attendance/api/eod_serializers.py`
- `attendance/api/eod_views.py`
- `attendance/api/urls.py`
- `docs/EOD_API_DOCUMENTATION.md`

---

## 4️⃣ RESTART PRODUCTION SERVER

### If using Systemd:
```bash
sudo systemctl restart smartpunch
```

### If using Gunicorn with Supervisor:
```bash
sudo supervisorctl restart smartpunch
```

### If using manual process:
```bash
pkill -f "python manage.py runserver"
python manage.py runserver 0.0.0.0:8000
```

---

## 5️⃣ TEST IN PRODUCTION

Replace `your-api-key` and `yourdomain.com` with actual values:

### Test Employee Endpoint:
```bash
curl -H "X-API-Key: your-api-key" \
  https://smartpunch.yourdomain.com/attendance/api/eod/employees/
```

**Expected Response (HTTP 200):**
```json
{
  "employees": [
    {
      "employee_id": "AI0021",
      "first_name": "Gali",
      "last_name": "Giridhareswar",
      "department": "Information Technology",
      "designation": "Full Stack Developer"
    }
  ]
}
```

### Test Attendance Endpoint:
```bash
curl -H "X-API-Key: your-api-key" \
  "https://smartpunch.yourdomain.com/attendance/api/eod/attendance/?date=2026-10-05"
```

**Expected Response (HTTP 200):**
```json
{
  "date": "2026-10-05",
  "attendance": [
    {"employee_id": "AI0021", "status": "PRESENT"},
    {"employee_id": "AI0022", "status": "ABSENT"}
  ]
}
```

---

## 6️⃣ PROVIDE KEY TO EOD TEAM

### Information to Share:

**Endpoints:**
```
GET https://smartpunch.yourdomain.com/attendance/api/eod/employees/
GET https://smartpunch.yourdomain.com/attendance/api/eod/attendance/?date=YYYY-MM-DD
```

**Authentication:**
```
Header: X-API-Key: <provided-key>
```

**Documentation:**
- Share `docs/EOD_API_DOCUMENTATION.md` with EOD team
- Include status values: PRESENT, ABSENT, WFH, LEAVE
- Include date format: YYYY-MM-DD

**Security:**
- Send API key via secure channel (password manager, encrypted message)
- Do NOT send via email or Slack
- Do NOT commit key to their Git repo

---

## ✅ DEPLOYMENT CHECKLIST

Before going live:

- [ ] Production API key generated
- [ ] `.env` file updated with key
- [ ] Code deployed to production server
- [ ] Production server restarted
- [ ] Employee endpoint tested (HTTP 200)
- [ ] Attendance endpoint tested (HTTP 200)
- [ ] Wrong API key returns 401
- [ ] Missing date returns 400
- [ ] API key provided to EOD team securely
- [ ] Documentation shared with EOD team

---

## 🔍 MONITORING

### Check Logs

**Django logs:**
```bash
tail -f /path/to/logs/django.log
```

**NGINX logs:**
```bash
tail -f /var/log/nginx/access.log | grep "/attendance/api/eod"
```

### Watch for:
- ✅ HTTP 200 responses (successful)
- ⚠️ HTTP 401 responses (authentication issues)
- ⚠️ HTTP 400 responses (invalid date format)
- ❌ HTTP 500 responses (server errors - investigate immediately)

---

## 🐛 TROUBLESHOOTING

### Problem: HTTP 500 Error

**Check:**
```bash
tail -100 /path/to/logs/django.log
```

**Common causes:**
- EOD_API_KEY not set in .env
- Server not restarted after .env update
- Database connection issue

**Fix:**
```bash
# Verify .env has EOD_API_KEY
grep EOD_API_KEY /path/to/smartpunch/.env

# Restart server
sudo systemctl restart smartpunch
```

---

### Problem: HTTP 401 Unauthorized

**Possible causes:**
- Wrong API key
- Missing X-API-Key header
- EOD_API_KEY not set in production

**Test:**
```bash
# Should return 401:
curl https://smartpunch.yourdomain.com/attendance/api/eod/employees/

# Should return 200:
curl -H "X-API-Key: correct-key" \
  https://smartpunch.yourdomain.com/attendance/api/eod/employees/
```

---

### Problem: HTTP 400 Bad Request

**For attendance endpoint:**
- Missing `date` parameter
- Invalid date format (must be YYYY-MM-DD)

**Correct usage:**
```bash
# ✅ Correct:
?date=2026-10-05

# ❌ Wrong:
?date=05-10-2026
?date=2026/10/05
(no date parameter)
```

---

## 📞 SUPPORT CONTACTS

**For SmartPunch/API issues:**
- Check validation report: `EOD_API_PHASE1_VALIDATION_REPORT.md`
- Check fixes report: `EOD_API_FIXES_APPLIED.md`
- Review implementation: `EOD_API_PHASE1_IMPLEMENTATION_REPORT.md`

**For EOD integration issues:**
- Share API documentation with EOD team
- Verify their requests include X-API-Key header
- Check date format in their requests

---

## 🔐 SECURITY REMINDERS

1. **Never commit API key to Git**
2. **Use HTTPS only** (not HTTP)
3. **Monitor API usage** for unusual patterns
4. **Rotate API key** if compromised
5. **Keep .env file** with restricted permissions (chmod 600)

---

## 🚀 YOU'RE READY!

Everything is tested and verified. Just follow the 6 steps above.

**Total deployment time:** ~10 minutes

**Files to deploy:** 3 Python files + 1 documentation file

**Database changes:** None (zero migrations)

**Risk level:** Low (read-only API, fully tested)

---

**Good luck with your deployment! 🎉**
