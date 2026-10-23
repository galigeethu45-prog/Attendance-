# PRODUCTION DEPLOYMENT GUIDE - URGENT UI FIXES

**Date:** October 23, 2026  
**Version:** SmartPunch v2.1  
**Changes:** UI/UX Fixes (Name consistency, Blank page, Table overlap, Daily insights)

---

## ⚠️ IMPORTANT: EOD Integration EXCLUDED

**EOD (End of Day) integration work is NOT included in this deployment.**

All EOD-related files have been moved to:
```
📁 EOD_INTEGRATION_WORK/
```

**This folder should NOT be deployed to production.**

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### 1. Backup Current Production
- [ ] Backup production database
- [ ] Backup current code
- [ ] Document current version
- [ ] Test backup restoration procedure

### 2. Verify Test Environment
- [ ] All fixes tested in development
- [ ] Browser testing complete (Chrome, Firefox, Edge)
- [ ] Mobile responsiveness verified
- [ ] Performance testing complete

### 3. Prepare Deployment Package
- [ ] Only include files listed in this guide
- [ ] Verify EOD_INTEGRATION_WORK folder is excluded
- [ ] Check no .pyc or __pycache__ files included
- [ ] Verify .env file NOT included

---

## 📦 FILES TO DEPLOY

### Templates (8 files):
```
templates/leave_approval.html
templates/wfh_approval.html
templates/onsite_approval.html
templates/overtime_approval.html
templates/master_data_list.html
templates/hr_dashboard.html
templates/dashboard.html
templates/team_leader_dashboard.html
```

### Backend (1 file):
```
attendance/views.py
```

### CSS (1 file):
```
static/css/style.css
```

### API Configuration (1 file):
```
attendance/api/urls.py  (EOD routes commented out)
```

**Total:** 11 files

---

## 🚫 FILES TO EXCLUDE

### Do NOT deploy these:
```
❌ EOD_INTEGRATION_WORK/ (entire folder)
❌ End-OF-the-Day-main* (EOD project folder)
❌ .env (environment variables)
❌ __pycache__/ folders
❌ *.pyc files
❌ .git/ folder
❌ .kiro/ folder
❌ node_modules/ (if exists)
```

---

## 🔧 DEPLOYMENT STEPS

### Step 1: Stop Production Server
```bash
# SSH into production server
ssh user@production-server

# Navigate to project
cd /path/to/smartpunch

# Stop server (adjust based on your setup)
sudo systemctl stop gunicorn
# OR
sudo supervisorctl stop smartpunch
```

### Step 2: Backup Current Code
```bash
# Create backup
cp -r /path/to/smartpunch /backups/smartpunch_backup_$(date +%Y%m%d_%H%M%S)

# Verify backup
ls -la /backups/
```

### Step 3: Upload New Files
```bash
# From local machine, upload files
scp templates/*.html user@production:/path/to/smartpunch/templates/
scp attendance/views.py user@production:/path/to/smartpunch/attendance/
scp static/css/style.css user@production:/path/to/smartpunch/static/css/
scp attendance/api/urls.py user@production:/path/to/smartpunch/attendance/api/
```

**OR use Git:**
```bash
# On production server
git pull origin main

# Verify only these files changed
git diff HEAD~1 --name-only
```

### Step 4: Collect Static Files
```bash
# On production server
cd /path/to/smartpunch
source venv/bin/activate
python manage.py collectstatic --noinput
```

### Step 5: No Database Migrations Needed
```
✅ This deployment requires NO database migrations
✅ No model changes were made
✅ Skip: python manage.py migrate
```

### Step 6: Restart Production Server
```bash
# Restart server
sudo systemctl start gunicorn
# OR
sudo supervisorctl start smartpunch

# Verify server is running
sudo systemctl status gunicorn
# OR
sudo supervisorctl status smartpunch

# Check logs
tail -f /var/log/smartpunch/error.log
```

### Step 7: Verify Deployment
```bash
# Check website is accessible
curl https://your-domain.com

# Check for errors
tail -f /var/log/smartpunch/error.log
```

---

## ✅ POST-DEPLOYMENT VERIFICATION

### Test in Production (Quick Check):

**1. Name Consistency (2 minutes)**
- [ ] Login as HR
- [ ] Check Leave Approval → All names in Title Case
- [ ] Check Master Data → All names in Title Case
- [ ] Result: ✅ Pass / ❌ Fail

**2. Blank Page Fix (2 minutes)**
- [ ] Login as Team Leader
- [ ] Go to Leave Approval → All Requests
- [ ] Scroll through all requests
- [ ] Result: ✅ Pass / ❌ Fail

**3. Table Overlap (1 minute)**
- [ ] Login as HR
- [ ] Go to Master Data
- [ ] Check Email and Department columns
- [ ] Result: ✅ Pass / ❌ Fail

**4. Daily Insights (2 minutes)**
- [ ] Login as HR
- [ ] HR Dashboard → Reports tab
- [ ] Verify 8 stat cards display at top
- [ ] Verify charts appear below
- [ ] Result: ✅ Pass / ❌ Fail

**Total Test Time: ~7 minutes**

---

## 🔄 ROLLBACK PROCEDURE

If deployment fails:

### Option 1: Restore from Backup
```bash
# Stop server
sudo systemctl stop gunicorn

# Restore backup
rm -rf /path/to/smartpunch/*
cp -r /backups/smartpunch_backup_YYYYMMDD_HHMMSS/* /path/to/smartpunch/

# Restart server
sudo systemctl start gunicorn
```

### Option 2: Git Revert
```bash
# Find commit to revert to
git log --oneline

# Revert to previous version
git reset --hard <previous-commit-hash>

# Restart server
sudo systemctl restart gunicorn
```

---

## 📊 CHANGE SUMMARY

### What Changed:
1. ✅ Name formatting: Added `|title` filter to 34+ locations
2. ✅ CSS fixes: Removed height restrictions causing blank pages
3. ✅ Table layout: Fixed column widths to prevent overlap
4. ✅ Daily Insights: Added to Reports tab with 8 stat cards

### What Did NOT Change:
- ❌ No database schema changes
- ❌ No new dependencies
- ❌ No settings.py changes
- ❌ No URL pattern changes (except commenting out EOD routes)
- ❌ No authentication/security changes

---

## 🔐 SECURITY CHECKLIST

- [ ] .env file NOT in deployment package
- [ ] DEBUG = False in production settings
- [ ] ALLOWED_HOSTS configured correctly
- [ ] SECRET_KEY not exposed
- [ ] Database credentials secure
- [ ] HTTPS enabled
- [ ] Static files served correctly

---

## 📞 SUPPORT CONTACTS

**If deployment fails:**
1. Check error logs first
2. Verify all files uploaded correctly
3. Check file permissions (should be readable)
4. Verify Python environment activated
5. Check static files collected

**Common Issues:**
- **500 Error:** Check error logs, verify syntax
- **404 on static files:** Run collectstatic again
- **Names not Title Case:** Clear browser cache
- **Charts not loading:** Check browser console

---

## 📝 DEPLOYMENT LOG

**Deployment Date:** _____________________  
**Deployed By:** _____________________  
**Server:** _____________________  
**Start Time:** _____________________  
**End Time:** _____________________  
**Status:** ✅ Success / ❌ Failed  

**Files Deployed:**
- [ ] 8 Template files
- [ ] 1 Backend file (views.py)
- [ ] 1 CSS file
- [ ] 1 API config file

**Verification:**
- [ ] All 4 fixes working in production
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Users notified of updates

**Notes:**
_____________________________________________
_____________________________________________
_____________________________________________

**Sign-off:** _____________________

---

## 🎯 NEXT STEPS AFTER DEPLOYMENT

1. **Monitor for 24 hours**
   - Watch error logs
   - Check user feedback
   - Monitor performance metrics

2. **Gather User Feedback**
   - HR team feedback on Daily Insights
   - Team Leaders feedback on approval pages
   - General user feedback on name formatting

3. **Document Lessons Learned**
   - What went well
   - What could be improved
   - Update deployment procedure if needed

4. **Plan Next Features**
   - Review feature backlog
   - Prioritize next improvements
   - Schedule next deployment

---

## ⚠️ REMEMBER

**DO NOT DEPLOY EOD_INTEGRATION_WORK FOLDER**

This folder contains incomplete EOD integration work and should remain in development only.

When ready to integrate EOD in future:
1. Read: `EOD_INTEGRATION_WORK/EOD_SMARTPUNCH_INTEGRATION_ANALYSIS_CHECKPOINT.md`
2. Complete Phase 3 implementation
3. Test thoroughly in development
4. Create separate deployment plan

---

**End of Deployment Guide**

