@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"
if exist "%PYTHON_EXE%" goto run_reset

set "PYTHON_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%PYTHON_EXE%" goto run_reset

for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
  set "PYTHON_EXE=%%P"
  goto run_reset
)

for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do (
  set "PYTHON_EXE=%%P"
  goto run_reset
)

echo ERROR: Python was not found. Run start_backend.bat first or install Python 3.10+.
exit /b 1

:run_reset
"%PYTHON_EXE%" seed_demo_data.py --reset

