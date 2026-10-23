# QUICK REFERENCE - Production Deployment

## 🚀 Deploy These 11 Files

```
✅ templates/leave_approval.html
✅ templates/wfh_approval.html
✅ templates/onsite_approval.html
✅ templates/overtime_approval.html
✅ templates/master_data_list.html
✅ templates/hr_dashboard.html
✅ templates/dashboard.html
✅ templates/team_leader_dashboard.html
✅ attendance/views.py
✅ static/css/style.css
✅ attendance/api/urls.py
```

## ❌ Don't Deploy These

```
❌ EOD_INTEGRATION_WORK/ (entire folder)
❌ End-OF-the-Day-main* (entire folder)
❌ .env
❌ __pycache__/
```

## 📖 Read First

1. **PRODUCTION_DEPLOYMENT_GUIDE.md** ⭐ (Complete instructions)

## ⚡ Quick Deploy Steps

1. Backup production
2. Upload 11 files
3. Run `collectstatic`
4. Restart server
5. Test (7 minutes)

## ✅ Quick Test After Deploy

1. Login as HR
2. Check Leave Approval → Names in Title Case?
3. Check Master Data → Columns OK?
4. Go to Reports tab → Daily Insights visible?
5. Login as TL → All requests visible?

## 🔄 Quick Rollback

```bash
sudo systemctl stop gunicorn
cp -r /backups/latest/* /path/to/smartpunch/
sudo systemctl start gunicorn
```

## 📞 If Problems

1. Check logs: `tail -f /var/log/smartpunch/error.log`
2. Rollback immediately if critical
3. Fix and redeploy

---

**Time:** ~20 minutes | **Risk:** Low | **Migrations:** None needed
