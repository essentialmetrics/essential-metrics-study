@echo off
cd c:/opt/essential-metrics
"C:\\opt\\essential-metrics\\virtual-env\\Scripts\\python.exe" c:/opt/essential-metrics/index.py
timeout /t 6 /nobreak >nul
start http://127.0.0.1:8050/home