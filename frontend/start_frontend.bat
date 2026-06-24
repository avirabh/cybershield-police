@echo off
setlocal
setlocal EnableDelayedExpansion
cd /d "%~dp0"

where npm.cmd >nul 2>nul
if errorlevel 1 (
  echo.
  echo ERROR: npm was not found.
  echo Install Node.js 18 or newer from https://nodejs.org/
  echo Then run this file again: start_frontend.bat
  echo.
  exit /b 1
)

echo Installing frontend dependencies...
call npm.cmd install
if errorlevel 1 (
  echo.
  echo ERROR: Frontend dependency installation failed.
  echo Check your internet connection, then run this file again.
  echo.
  exit /b 1
)

set "FRONTEND_PORT=5173"
set "PORT_PID="
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%FRONTEND_PORT% .*LISTENING"') do (
  set "PORT_PID=%%P"
)

if defined PORT_PID (
  echo.
  echo Port %FRONTEND_PORT% is already in use by process %PORT_PID%.
  set /p STOP_OLD="Stop the existing frontend server and restart it? (Y/N): "
  if /I "!STOP_OLD!"=="Y" (
    taskkill /F /PID !PORT_PID!
    if errorlevel 1 (
      echo.
      echo ERROR: Could not stop process !PORT_PID!. Close the old frontend terminal manually and run this file again.
      echo.
      exit /b 1
    )
    timeout /t 2 /nobreak >nul
  ) else (
    echo.
    echo Keeping the existing frontend server. Open http://127.0.0.1:%FRONTEND_PORT% in your browser.
    echo.
    exit /b 0
  )
)

echo Building frontend production demo...
call npm.cmd run build
if errorlevel 1 (
  echo.
  echo ERROR: Frontend build failed.
  echo Check the error above, then run this file again.
  echo.
  exit /b 1
)

echo Starting CyberShield Police frontend at http://127.0.0.1:5173
call npm.cmd run preview
