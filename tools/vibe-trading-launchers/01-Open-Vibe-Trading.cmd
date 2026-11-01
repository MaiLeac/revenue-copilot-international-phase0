@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0VibeTrading.ps1" -Action Start
if errorlevel 1 (pause & exit /b 1)
