@echo off
setlocal EnableDelayedExpansion
set "BACKEND_PORT=8000"
set "FOUND="

for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%BACKEND_PORT% .*LISTENING"') do (
  set "FOUND=1"
  echo Stopping backend process %%P on port %BACKEND_PORT%...
  taskkill /F /PID %%P
)

if not defined FOUND (
  echo No backend server is running on port %BACKEND_PORT%.
)

