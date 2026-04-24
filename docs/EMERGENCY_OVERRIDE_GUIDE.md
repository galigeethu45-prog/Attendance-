# 🚨 Emergency Override Feature - Complete Guide

## Overview

The **Emergency Override** feature allows HR to temporarily bypass IP-based office network restrictions, enabling all employees to check-in from any location. This is designed for emergency situations when the office network (Regus) is down or inaccessible.

---

## 🎯 Purpose

### When to Use
- ✅ Regus office network is down
- ✅ ISP issues preventing office connectivity
- ✅ Network maintenance or upgrades
- ✅ Emergency situations requiring remote work
- ✅ Temporary office closure

### When NOT to Use
- ❌ Individual employee requests
- ❌ Regular remote work (use WFH approval instead)
- ❌ Testing purposes
- ❌ Convenience (proper WFH process should be followed)

---

## 🔐 Access Control

### Who Can Enable/Disable
- ✅ **HR users** (users with `is_hr=True`)
- ✅ **Superusers** (Django admin users)

### Who Benefits
- 👥 **ALL employees** can check-in from any location when enabled
- 🌍 Bypasses IP restrictions for everyone
- 📍 No location validation performed

---

## 🚀 How to Use

### For HR: Enabling Emergency Override

1. **Login as HR user**
   - Navigate to HR Dashboard

2. **Click "Emergency Override" button**
   - Located at top-right of HR Dashboard
   - Button shows current status

3. **Provide Reason**
   - Enter clear reason (e.g., "Regus network down")
   - Reason is logged in audit trail
   - Required field

4. **Click "Enable Override"**
   - Confirm the action
   - System immediately activates override
   - All employees notified via check-in message

5. **Verify Status**
   - Button turns yellow/warning color
   - Shows "🚨 Override ACTIVE"
   - Status visible in modal

### For HR: Disabling Emergency Override

1. **Click "Emergency Override" button**
   - Opens status modal

2. **Click "Disable Override"**
   - Confirm the action
   - Normal IP restrictions restored

3. **Verify Status**
   - Button returns to normal color
   - Shows "Emergency Override"
   - Employees must follow normal rules

### For Employees: During Override

1. **Check-in as normal**
   - No special action required
   - Can check-in from anywhere

2. **Check-in message shows**
   - "🚨 Emergency Override Active - Network restrictions bypassed"
   - Indicates override is in effect

3. **No WFH approval needed**
   - Override bypasses all location checks
   - Works from home, cafe, anywhere

---

## 🔄 How It Works

### Priority Order (Check-in Validation)

1. **Emergency Override** (Highest Priority)
   - If enabled: ✅ Allow from anywhere
   - Bypasses all other checks

2. **HR/Admin**
   - Always allowed from anywhere

3. **Work Mode**
   - Hybrid: Allowed from anywhere
   - Permanent WFH: Allowed from anywhere
   - Office: Continue to next check

4. **Office Network**
   - If on Regus IP: ✅ Allow
   - If not: Continue to next check

5. **Approved WFH**
   - If has approved WFH for today: ✅ Allow
   - If not: ❌ Deny

### Technical Implementation

```python
# Check order in can_check_in_from_location()
1. Check emergency override → Allow if enabled
2. Check HR/Admin → Allow
3. Check work mode → Allow if hybrid/permanent_wfh
4. Check office IP → Allow if on Regus network
5. Check WFH approval → Allow if approved
6. Deny → Must be on office network or have WFH
```

---

## 📊 Audit Trail

### What Gets Logged

Every emergency override action is logged:

**When Enabled:**
- ✅ Who enabled it (HR user)
- ✅ When it was enabled (timestamp)
- ✅ Reason provided
- ✅ IP address of HR user
- ✅ Action: "Emergency Override ENABLED"

**When Disabled:**
- ✅ Who disabled it (HR user)
- ✅ When it was disabled (timestamp)
- ✅ IP address of HR user
- ✅ Action: "Emergency Override DISABLED"

### Viewing Audit Logs

1. **Django Admin**
   - Go to: `/admin/attendance/auditlog/`
   - Filter by action: "system_setting_change"

2. **Database Query**
   ```python
   from attendance.models import AuditLog
   
   # Get override actions
   override_logs = AuditLog.objects.filter(
       action='system_setting_change',
       description__icontains='Emergency Override'
   )
   ```

---

## 🎨 UI Indicators

### HR Dashboard Button

**When Disabled (Normal):**
- Color: Outline white
- Text: "Emergency Override"
- Icon: ⚠️ Warning triangle

**When Enabled (Active):**
- Color: Yellow/Warning
- Text: "🚨 Override ACTIVE"
- Icon: ⚠️ Warning triangle
- Pulsing animation

### Modal Dialog

**Status Display:**
- Green alert: Override disabled (normal)
- Yellow alert: Override enabled (active)
- Shows who enabled, when, and why

**Controls:**
- Reason textarea (required for enabling)
- Enable button (yellow)
- Disable button (green)
- Information panel explaining feature

### Employee Check-in

**When Override Active:**
- Check-in success message includes:
  - "🚨 Emergency Override Active"
  - "Network restrictions bypassed"

---

## 🔧 Technical Details

### Database Model

**Table:** `attendance_systemsettings`

**Fields:**
- `id` - Always 1 (singleton pattern)
- `emergency_override_enabled` - Boolean
- `emergency_override_reason` - Text
- `emergency_override_enabled_by` - Foreign key to User
- `emergency_override_enabled_at` - DateTime
- `last_updated` - DateTime (auto)
- `last_updated_by` - Foreign key to User

### API Endpoints

**Get Status (AJAX):**
```
GET /attendance/emergency-override/status/
Response: {
    "enabled": true/false,
    "reason": "string",
    "enabled_by": "string",
    "enabled_at": "datetime"
}
```

**Toggle Override (POST):**
```
POST /attendance/emergency-override/toggle/
Data: {
    "action": "enable" or "disable",
    "reason": "string" (required for enable)
}
```

### Code Locations

**Model:** `attendance/models.py` - `SystemSettings` class
**Views:** `attendance/views.py` - `toggle_emergency_override()`, `emergency_override_status()`
**URLs:** `attendance/urls.py` - Emergency override routes
**Template:** `templates/hr_dashboard.html` - Modal and JavaScript
**Admin:** `attendance/admin.py` - SystemSettings admin

---

## 🧪 Testing

### Test Scenario 1: Enable Override

1. Login as HR user
2. Click "Emergency Override" button
3. Enter reason: "Testing emergency override"
4. Click "Enable Override"
5. Verify button turns yellow
6. Logout

7. Login as regular employee (from home)
8. Try to check-in
9. Should succeed with override message
10. Verify check-in recorded

### Test Scenario 2: Disable Override

1. Login as HR user
2. Click "Emergency Override" button
3. Click "Disable Override"
4. Verify button returns to normal
5. Logout

6. Login as regular employee (from home)
7. Try to check-in
8. Should fail with IP restriction message

### Test Scenario 3: Audit Trail

1. Enable override
2. Disable override
3. Go to Django admin: `/admin/attendance/auditlog/`
4. Filter by "system_setting_change"
5. Verify both actions logged with details

---

## 🛡️ Security Considerations

### Access Control
- ✅ Only HR and superusers can toggle
- ✅ Regular employees cannot access
- ✅ Unauthorized attempts logged

### Audit Trail
- ✅ All actions logged with timestamp
- ✅ User who made change recorded
- ✅ IP address captured
- ✅ Reason required and stored

### Best Practices
- ✅ Disable immediately when network restored
- ✅ Provide clear, specific reasons
- ✅ Monitor audit logs regularly
- ✅ Review override usage monthly
- ✅ Train HR on proper usage

---

## 📝 Best Practices

### For HR

1. **Use Sparingly**
   - Only for genuine emergencies
   - Not for convenience

2. **Provide Clear Reasons**
   - Be specific: "Regus network down since 9 AM"
   - Not vague: "Network issue"

3. **Disable Promptly**
   - As soon as network restored
   - Don't leave enabled overnight

4. **Communicate**
   - Inform employees when enabled
   - Notify when disabled
   - Use company communication channels

5. **Monitor**
   - Check who's checking in during override
   - Review audit logs
   - Report any misuse

### For Employees

1. **Check Status**
   - Look for override message during check-in
   - Don't assume it's always enabled

2. **Follow Normal Process**
   - Use WFH approval for planned remote work
   - Override is for emergencies only

3. **Report Issues**
   - If override seems enabled unnecessarily
   - If you can't check-in when it should be enabled

---

## 🔍 Troubleshooting

### Override Not Working

**Problem:** Enabled override but employees still can't check-in

**Solutions:**
1. Verify override is actually enabled:
   - Check HR dashboard button color
   - Open modal and verify status

2. Check employee work mode:
   - If "office" mode, override should work
   - If already "hybrid/permanent_wfh", they don't need override

3. Clear browser cache:
   - Employee may have cached old status
   - Hard refresh (Ctrl+F5)

4. Check server logs:
   - Look for errors in Django console
   - Verify database updated

### Can't Enable Override

**Problem:** HR user can't enable override

**Solutions:**
1. Verify HR status:
   - Check `is_hr=True` in employee profile
   - Or user is superuser

2. Check permissions:
   - Verify user is logged in
   - Check session hasn't expired

3. Check reason field:
   - Must provide reason to enable
   - Cannot be empty

### Button Not Showing

**Problem:** Emergency override button not visible

**Solutions:**
1. Verify user is HR:
   - Only HR sees the button
   - Regular employees don't have access

2. Check template:
   - Verify `hr_dashboard.html` updated
   - Clear template cache

3. Hard refresh:
   - Ctrl+F5 to reload page
   - Clear browser cache

---

## 📊 Monitoring & Reports

### Daily Checks

1. **Morning Check**
   - Verify override is disabled (unless needed)
   - Check for any overnight changes

2. **During Override**
   - Monitor who's checking in
   - Verify legitimate usage

3. **End of Day**
   - Disable if network restored
   - Review audit logs

### Weekly Review

1. **Audit Log Review**
   - Check all override actions
   - Verify reasons provided
   - Look for patterns

2. **Usage Statistics**
   - How often enabled?
   - Average duration?
   - Which HR users toggling?

### Monthly Report

1. **Generate Report**
   ```python
   from attendance.models import AuditLog
   from django.utils import timezone
   from datetime import timedelta
   
   # Last 30 days
   thirty_days_ago = timezone.now() - timedelta(days=30)
   
   override_actions = AuditLog.objects.filter(
       action='system_setting_change',
       description__icontains='Emergency Override',
       timestamp__gte=thirty_days_ago
   )
   
   print(f"Total override actions: {override_actions.count()}")
   for log in override_actions:
       print(f"{log.timestamp}: {log.description} by {log.user}")
   ```

2. **Review Metrics**
   - Total times enabled
   - Average duration
   - Most common reasons
   - Trends over time

---

## 🎓 Training Guide

### For HR Users

**Training Checklist:**
- [ ] Understand purpose of emergency override
- [ ] Know when to use vs. WFH approval
- [ ] Practice enabling/disabling
- [ ] Learn to provide clear reasons
- [ ] Understand audit trail
- [ ] Know how to verify status
- [ ] Practice emergency scenarios

**Training Scenarios:**
1. Regus network down at 9 AM
2. ISP outage during work hours
3. Planned network maintenance
4. Emergency remote work day

### For Employees

**What to Know:**
- Override is for emergencies only
- Use WFH approval for planned remote work
- Check-in message will indicate override active
- Normal rules apply when disabled

---

## 📞 Support

### Common Questions

**Q: Can I enable override for just one employee?**
A: No, override affects all employees. Use WFH approval for individual cases.

**Q: How long should override stay enabled?**
A: Only as long as the emergency lasts. Disable immediately when resolved.

**Q: Can employees see override status?**
A: Yes, check-in message shows when override is active.

**Q: Is override logged?**
A: Yes, all actions logged in audit trail with full details.

**Q: Can I schedule override in advance?**
A: No, it's for emergencies. Use WFH approval for planned remote work.

---

## ✅ Summary

### Key Points

1. **Emergency Use Only**
   - For network outages and emergencies
   - Not for regular remote work

2. **HR Control**
   - Only HR can enable/disable
   - Requires reason for enabling

3. **All Employees Affected**
   - Bypasses IP restrictions for everyone
   - No individual control

4. **Fully Audited**
   - All actions logged
   - Who, when, why recorded

5. **Easy to Use**
   - One-click enable/disable
   - Clear status indicators

### Quick Reference

| Action | Who | Where | Result |
|--------|-----|-------|--------|
| Enable | HR | HR Dashboard → Emergency Override | All can check-in anywhere |
| Disable | HR | HR Dashboard → Emergency Override | Normal IP restrictions |
| Check Status | HR | HR Dashboard button color | Yellow = Active, White = Disabled |
| View Logs | HR/Admin | Django Admin → Audit Logs | All override actions |

---

**Feature Status:** ✅ Fully Implemented and Tested  
**Version:** 1.0  
**Last Updated:** April 22, 2026
