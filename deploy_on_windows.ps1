# deploy_on_windows.ps1
# Automates the deployment of the MintFlow Streamlit Dashboard as a Windows Background Service.
# This script must be run from an Elevated (Administrator) PowerShell prompt.

# 1. Check for Administrator Privileges
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This script MUST be run from an Elevated (Administrator) PowerShell prompt!"
    Write-Host "`n[ERROR] Please right-click PowerShell, select 'Run as Administrator', and execute this script again.`n" -ForegroundColor Red
    Exit
}

# 2. Define Variables
$serviceName = "MintFlowAssistant"
$zipPath = Join-Path $PSScriptRoot "nssm-2.24.zip"
$extractDir = Join-Path $PSScriptRoot "bin"
$nssmExe = Join-Path $extractDir "nssm-2.24\win64\nssm.exe"

# 3. Download and Extract NSSM (Non-Sucking Service Manager)
if (-not (Test-Path $nssmExe)) {
    Write-Host "`n--- Downloading NSSM (Non-Sucking Service Manager) ---" -ForegroundColor Cyan
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    
    try {
        # Force TLS 1.2/1.3 for secure download
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $nssmUrl -OutFile $zipPath -UseBasicParsing -ErrorAction Stop
        
        Write-Host "Extracting files to: $extractDir ..." -ForegroundColor Cyan
        Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force
        
        # Verify extraction
        if (-not (Test-Path $nssmExe)) {
            $nssmExe = Join-Path $extractDir "nssm-2.24\win32\nssm.exe"
        }
        
        if (-not (Test-Path $nssmExe)) {
            throw "nssm.exe was not found in the extracted directory structure."
        }
        
        # Clean up zip file
        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
        Write-Host "NSSM binary extracted successfully." -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to download/extract NSSM: $_"
        Write-Host "`nPlease download nssm.exe manually, place it inside a 'bin' directory in the project root, and re-run this script.`n" -ForegroundColor Yellow
        Exit
    }
} else {
    Write-Host "`nNSSM binary already exists in 'bin' directory. Skipping download." -ForegroundColor Green
}

# 4. Resolve Python Path
$pythonPath = ""
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonPath = (Get-Command python).Source
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonPath = (Get-Command py).Source
}

if (-not $pythonPath) {
    Write-Error "Python was not found on your system PATH!"
    Write-Host "Please install Python or ensure it is added to the System environment variables." -ForegroundColor Red
    Exit
}

Write-Host "Using Python executable: $pythonPath" -ForegroundColor Green

# 5. Install and Configure Windows Service
Write-Host "`n--- Registering Windows Service: '$serviceName' ---" -ForegroundColor Cyan
$appPath = Join-Path $PSScriptRoot "app.py"
$arguments = "-m streamlit run `"$appPath`" --server.port 8599 --server.address 127.0.0.1"

# Stop and Remove existing service if it exists to allow reconfiguration
& $nssmExe stop $serviceName 2>$null | Out-Null
& $nssmExe remove $serviceName confirm 2>$null | Out-Null

# Register Service parameters
try {
    # Install the service with target application and args
    & $nssmExe install $serviceName `"$pythonPath`" $arguments | Out-Null
    
    # Set app working directory (vital for imports and local data files)
    & $nssmExe set $serviceName AppDirectory `"$PSScriptRoot`" | Out-Null
    
    # Set description and automatic startup configurations
    & $nssmExe set $serviceName Description "MintFlow Mutual Fund FAQ Assistant RAG App Server" | Out-Null
    & $nssmExe set $serviceName Start SERVICE_AUTO_START | Out-Null
    
    Write-Host "Service '$serviceName' successfully installed." -ForegroundColor Green
}
catch {
    Write-Error "Failed to configure Windows Service: $_"
    Exit
}

# 6. Start the Service
Write-Host "`n--- Starting Service: '$serviceName' ---" -ForegroundColor Cyan
try {
    & $nssmExe start $serviceName | Out-Null
    
    Write-Host "`n======================================================================" -ForegroundColor Green
    Write-Host "MINTFLOW ASSISTANT WINDOWS SERVICE STARTED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "Dashboard URL : http://localhost:8599" -ForegroundColor Green
    Write-Host "Service Status: Running (Automatic Startup on Boot)" -ForegroundColor Green
    Write-Host "To manage the service, open Services desktop app (services.msc)" -ForegroundColor Green
    Write-Host "or use nssm commands: bin\nssm-2.24\win64\nssm.exe <status/start/stop> $serviceName" -ForegroundColor Green
    Write-Host "======================================================================`n" -ForegroundColor Green
}
catch {
    Write-Warning "Service was installed but failed to start automatically: $_"
    Write-Host "You can start it manually using: Start-Service $serviceName" -ForegroundColor Yellow
}
