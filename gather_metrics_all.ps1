# This script will run every hour to gather metrics on the system.
Set-Location C:\opt\essential-metrics

& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\utils\database_class.py"

& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_1_asset_register.py"
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
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_13_antivirus_working.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_14_threat_scanning.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_15_external_ports.py"

# EM_16 is captured in EM_1 automation
# & "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_17_event_ids.py"
# & "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_17_firewall_log.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_18_rdp_settings.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_19_usb_attached.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_20_admin_logins.py"
& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\EM_20_users_and_groups.py"

& "C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" "C:\opt\essential-metrics\collect_system_metrics.py"