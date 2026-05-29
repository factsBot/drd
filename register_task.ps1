# PowerShell script to register Daily Industry News Digest with Windows Task Scheduler
# Run this script to schedule the digest at 5:00 AM every single morning.

$TaskName = "DailyIndustryDigest"
$ScriptPath = "C:\Users\goldonil\.projects\drd\run_digest.bat"
$WorkDir = "C:\Users\goldonil\.projects\drd"

Write-Host "=== Registering Daily Industry News Digest Task ===" -ForegroundColor Cyan

# 1. Check if batch file exists
if (-not (Test-Path $ScriptPath)) {
    Write-Error "Could not find batch script at $ScriptPath. Please make sure the folder path is correct."
    exit 1
}

# 2. Define scheduled task action
Write-Host "Configuring action: Run $ScriptPath" -ForegroundColor Gray
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$ScriptPath`"" -WorkingDirectory $WorkDir

# 3. Define daily trigger at 5:00 AM
Write-Host "Configuring daily trigger at 5:00 AM..." -ForegroundColor Gray
$Trigger = New-ScheduledTaskTrigger -Daily -At "5:00 AM"

# 4. Configure robust settings (run if missed, allow batteries, don't stop)
Write-Host "Configuring operational settings..." -ForegroundColor Gray
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 5. Register the task under the current user context
Write-Host "Registering scheduled task '$TaskName'..." -ForegroundColor Gray
try {
    # Force registration to overwrite if it already exists
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Runs the morning industry news digest aggregator at 5:00 AM daily." -Force | Out-Null
    Write-Host "[SUCCESS] Task '$TaskName' has been successfully registered!" -ForegroundColor Green
    Write-Host "It is scheduled to run every day at 5:00 AM." -ForegroundColor Green
    Write-Host "To verify or trigger it manually, open Windows Task Scheduler and locate 'DailyIndustryDigest' in the library." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to register task: $_" -ForegroundColor Red
    Write-Host "Note: You may need to run PowerShell as an Administrator to register scheduled tasks." -ForegroundColor Yellow
}
