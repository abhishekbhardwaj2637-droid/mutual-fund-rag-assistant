# setup_scheduler.ps1
# PowerShell script to register the Mutual Fund Ingestion Pipeline as a daily Windows Scheduled Task.

# Ensure script is running with administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "This script should be run as Administrator to register a system-wide Scheduled Task."
    Write-Warning "Please relaunch PowerShell as Administrator and run this script again if the registration fails."
}

# Define Task parameters
$TaskName = "MutualFundFAQ_IngestionPipeline"
$Description = "Daily ingestion pipeline for Mutual Fund FAQ RAG Assistant. Fetches, parses, and loads scheme pages from Groww into ChromaDB."
$WorkingDirectory = $PSScriptRoot

# Find python executable (prefer py.exe launcher on Windows, otherwise python.exe)
$PythonPath = (Get-Command py.exe -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    $PythonPath = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
}
if (-not $PythonPath) {
    $PythonPath = "py.exe" # Fallback to path resolution at runtime
}

Write-Host "Project Directory: $WorkingDirectory"
Write-Host "Python Executable: $PythonPath"

# Define the script path
$ScriptPath = Join-Path $WorkingDirectory "ingestion\run_pipeline.py"
$Arguments = "`"$ScriptPath`""

# Create Action
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $Arguments -WorkingDirectory $WorkingDirectory

# Create Trigger (Daily at 10:00 AM)
$Trigger = New-ScheduledTaskTrigger -Daily -At 10:00AM

# Create Settings (Allow start on battery power, run as soon as possible after missed trigger, and retry up to 3 times on failure)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 15)

# Register the Scheduled Task
try {
    # Check if task already exists and unregister it if it does
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "Existing scheduled task '$TaskName' found. Overwriting..."
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description $Description
    
    Write-Host "--------------------------------------------------------" -ForegroundColor Green
    Write-Host "Scheduled Task '$TaskName' registered successfully!" -ForegroundColor Green
    Write-Host "It is configured to run daily at 10:00 AM." -ForegroundColor Green
    Write-Host "Working Directory: $WorkingDirectory" -ForegroundColor Green
    Write-Host "Python Command: $PythonPath $Arguments" -ForegroundColor Green
    Write-Host "To run it manually for testing, execute:" -ForegroundColor Green
    Write-Host "  Start-ScheduledTask -TaskName `"$TaskName`"" -ForegroundColor Green
    Write-Host "To check the task status, execute:" -ForegroundColor Green
    Write-Host "  Get-ScheduledTask -TaskName `"$TaskName`"" -ForegroundColor Green
    Write-Host "--------------------------------------------------------" -ForegroundColor Green
}
catch {
    Write-Error "Failed to register scheduled task: $_"
}
