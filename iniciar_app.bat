@echo off
title Wellness Routine Manager

echo Iniciando backend...
start "Wellness Backend" cmd /k "cd /d "IsWellnessBackend-main" && uvicorn main:app --host 127.0.0.1 --port 8000"

echo Esperando a que el backend este listo...
timeout /t 5 /nobreak >nul

echo Iniciando aplicacion...
start "Wellness App" cmd /k "cd /d "IsWellness-main" && flet run"

echo Listo. La aplicacion se abrira en unos segundos.
exit