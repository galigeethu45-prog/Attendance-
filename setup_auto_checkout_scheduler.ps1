# PowerShell script to setup Windows Task Scheduler for Auto Checkout
# Run this as Administrator

$taskName = "Attendance Auto Checkout"
$scriptPath = Join-Path $PSScriptRoot "run_auto_checkout.bat"
$time = "19:00"  # 7:00 PM

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Setting up Auto Checkout Task Scheduler" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create the scheduled task action
$action = New-ScheduledTaskAction -Execute $scriptPath

# Create the trigger (daily at 7 PM)
$trigger = New-ScheduledTaskTrigger -Daily -At $time

# Create the task settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register the scheduled task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Automatically checks out employees at 7 PM if they forgot to check out"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Task Scheduler Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Task Name: $taskName" -ForegroundColor White
Write-Host "Run Time: $time (7:00 PM) daily" -ForegroundColor White
Write-Host "Script: $scriptPath" -ForegroundColor White
Write-Host ""
Write-Host "To view the task:" -ForegroundColor Yellow
Write-Host "1. Open Task Scheduler (taskschd.msc)" -ForegroundColor Yellow
Write-Host "2. Look for '$taskName' in Task Scheduler Library" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test manually, run:" -ForegroundColor Cyan
Write-Host "  python manage.py auto_checkout" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Your computer must be ON at 7 PM for this to work!" -ForegroundColor Red
Write-Host ""

Read-Host "Press Enter to exit"
