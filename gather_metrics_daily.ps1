# This script will run every day to gather metrics on the system.
Set-Location C:\opt\essential-metrics

& "C:\\Program Files\\Python311\\python.exe" "C:\opt\essential-metrics\EM_1_asset_register.py"
& "C:\\Program Files\\Python311\\python.exe" "C:\opt\essential-metrics\EM_13_antivirus_working.py"
& "C:\\Program Files\\Python311\\python.exe" "C:\opt\essential-metrics\EM_15_external_ports.py"
& "C:\\Program Files\\Python311\\python.exe" "C:\opt\essential-metrics\EM_18_rdp_settings.py"
& "C:\\Program Files\\Python311\\python.exe" "C:\opt\essential-metrics\EM_19_usb_attached.py"