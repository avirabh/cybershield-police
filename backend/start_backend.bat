@echo off
setlocal
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "PYTHON_EXE="

if exist "%CD%\.venv\Scripts\python.exe" (
  set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"
  goto install_deps
)

for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
  set "PYTHON_EXE=%%P"
  goto create_venv
)

for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do (
  set "PYTHON_EXE=%%P"
  goto create_venv
)

for %%P in (
  "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
  "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  "C:\Python313\python.exe"
  "C:\Python312\python.exe"
  "C:\Python311\python.exe"
) do (
  if exist "%%~P" (
    set "PYTHON_EXE=%%~P"
    goto create_venv
  )
)

echo.
echo ERROR: Python was not found.
echo Install Python 3.10 or newer from https://www.python.org/downloads/
echo During installation, select "Add python.exe to PATH".
echo Then run this file again: start_backend.bat
echo.
exit /b 1

:create_venv
echo Using Python: %PYTHON_EXE%
echo Creating backend virtual environment...
"%PYTHON_EXE%" -m venv --system-site-packages .venv
if errorlevel 1 (
  echo.
  echo ERROR: Could not create .venv. Please install Python 3.10 or newer and run this file again.
  echo.
  exit /b 1
)

set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"

:install_deps
echo Installing backend dependencies...
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo ERROR: Dependency installation failed.
  echo Check your internet connection, then run this file again.
  echo.
  exit /b 1
)

set "BACKEND_PORT=8000"
set "PORT_PID="
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%BACKEND_PORT% .*LISTENING"') do (
  set "PORT_PID=%%P"
)

if defined PORT_PID (
  echo.
  echo Port %BACKEND_PORT% is already in use by process %PORT_PID%.
  set /p STOP_OLD="Stop the existing backend server and restart it? (Y/N): "
  if /I "!STOP_OLD!"=="Y" (
    taskkill /F /PID !PORT_PID!
    if errorlevel 1 (
      echo.
      echo ERROR: Could not stop process !PORT_PID!. Close the old backend terminal manually and run this file again.
      echo.
      exit /b 1
    )
    timeout /t 2 /nobreak >nul
  ) else (
    echo.
    echo Keeping the existing backend server. API is at http://127.0.0.1:%BACKEND_PORT%
    echo.
    exit /b 0
  )
)

echo Starting CyberShield Police backend at http://127.0.0.1:8000
"%PYTHON_EXE%" run_backend.py
