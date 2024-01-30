# This Powershell script will configure the system.
# Install python

# just local install
Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe" -OutFile "C:\\Users\\John\\Desktop\\git.exe"

mkdir C:\opt\essential-metrics
mkdir C:\opt\installs






Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe" -OutFile "C:\\opt\\installs\\python-3.12.1-amd64.exe"
Invoke-WebRequest -Uri "https://npcap.com/dist/npcap-1.79.exe" -OutFile "C:\\opt\\installs\\npcap-1.79.exe"
Invoke-WebRequest -Uri "https://nmap.org/dist/nmap-7.94-setup.exe" -OutFile "C:\\opt\\installs\\nmap-7.94-setup.exe"

Invoke-WebRequest -Uri "https://download.sqlitebrowser.org/DB.Browser.for.SQLite-3.12.2-win64.msi" -OutFile "C:\\opt\\installs\\DB.Browser.for.SQLite-3.12.2-win64.msi"

Set-Location C:\opt\
git clone git@github.com:essentialmetrics/essential-metrics.git

Set-Location C:\opt\installs
.\python-3.12.1-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
.\nmap-7.94-setup.exe /S

sleep 60

Set-Location C:\opt\essential-metrics
& "C:/Program Files/Python312/python.exe" -m venv virtual-env

.\virtual-env\Scripts\pip install -r .\requirements.txt


# Fix the broken public python module

$content = Get-Content .\virtual-env\Lib\site-packages\pyreadline\py3k_compat.py
$content = $content -replace "isinstance\(x, collections.Callable\)", "isinstance(x, collections.abc.Callable)"
Set-Content .\virtual-env\Lib\site-packages\pyreadline\py3k_compat.py -Value $content


Invoke-WebRequest -Uri "https://github.com/nmap/nmap.git" -OutFile "C:\\opt\\nmap\\nmap.git"



Set-ExecutionPolicy RemoteSigned -Scope Process


# Domain specific
# Set-NetFirewallProfile -Profile Domain -LogMaxSizeKilobytes 10240

# Configure Firewall

Set-NetFirewallProfile -LogMaxSizeKilobytes 10240
Set-NetFirewallProfile -LogBlocked True
Set-NetFirewallProfile -LogAllowed True
Set-NetFirewallProfile -Enabled True


# Configure policy event logs for logon
Auditpol /set /subcategory:"Logon" /success:enable /failure:enable
Auditpol /set /subcategory:"Logoff" /success:enable /failure:disable

AuditPol /get /category:"Logon/Logoff"

# Configure policy event logs for process creation
auditpol /set /subcategory:"Process Creation" /success:enable /failure:disable
auditpol /set /subcategory:"Process Termination" /success:enable /failure:disable

auditpol /get /subcategory:"Process Creation"
auditpol /get /subcategory:"Process Termination"




# Configure the scheduled task to collect hourly metrics
$Action = New-ScheduledTaskAction -Execute 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -Argument '-File "C:\opt\essential-metrics\gather_metrics_hourly.ps1"'
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 10000)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
Register-ScheduledTask -TaskName "GatherEssentialMetricsHourly" -Action $Action -Trigger $Trigger -Principal $Principal


# Configure the scheduled task to collect daily metrics
$Action = New-ScheduledTaskAction -Execute 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -Argument '-File "C:\opt\essential-metrics\gather_metrics_daily.ps1"'
$Trigger = New-ScheduledTaskTrigger -Daily -At '11:15'
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
$Settings = New-ScheduledTaskSettingsSet
$Settings.StartWhenAvailable = $true
Register-ScheduledTask -TaskName "GatherEssentialMetricsDaily" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings
