# This script will run every hour to gather metrics on the system.
Set-Location C:\opt\essential-metrics

& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_2_software_register.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_3_firewall.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_4_scheduled_tasks.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_5_enabled_services.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_6_defender_updates.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_7_password_policy.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_8_wlan_settings.py" 
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_9_controlled_folder.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_10_onedrive_backup.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_11_vulnerability_patching.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_12_reboot_analysis.py"
# EM_13 runs daily
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_14_threat_scanning.py"
# EM_15 runs daily
# EM_16 is captured in EM_1 automation
# & "C:\\Program Files\\Python311\\python.exe" "C:\opt\essential-metrics\EM_17_event_ids.py"
# & "C:\\Program Files\\Python311\\python.exe" "C:\opt\essential-metrics\EM_17_firewall_log.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_20_admin_logins.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_20_users_and_groups.py"