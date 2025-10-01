@echo off
chcp 65001 >nul
cd /d "%~dp0"
python verificador_batt_dept.py
pause
