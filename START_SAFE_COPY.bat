@echo off
cd /d "%~dp0"
python safe_copy.py
if errorlevel 1 pause
