@echo off
setlocal EnableDelayedExpansion
set "FRONTEND_PORT=5173"
set "FOUND="

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%FRONTEND_PORT% .*LISTENING"') do (
  set "FOUND=1"
  echo Stopping frontend process %%P on port %FRONTEND_PORT%...
  taskkill /F /PID %%P
)

if not defined FOUND (
  echo No frontend server is running on port %FRONTEND_PORT%.
)

