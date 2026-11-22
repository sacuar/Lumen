@echo off
rem Usage: call select_python.bat [auto|3.12|3.14]
set "LUMEN_PY=%~1"
if "%LUMEN_PY%"=="" set "LUMEN_PY=auto"
if /i "%LUMEN_PY%"=="auto" (
  py -3.12 -c "import sys; assert sys.version_info[:2] == (3,12)" >nul 2>&1
  if not errorlevel 1 (set "LUMEN_PY=3.12") else (set "LUMEN_PY=3.14")
)
if not "%LUMEN_PY%"=="3.12" if not "%LUMEN_PY%"=="3.14" exit /b 1
py -%LUMEN_PY% -c "import sys; assert '%d.%d' %% sys.version_info[:2] == '%LUMEN_PY%'" >nul 2>&1
if errorlevel 1 (
 echo Requested Python unavailable. Install Python 3.12 or 3.14 with the py launcher.
 exit /b 1
)
set "LUMEN_VENV=.venv-%LUMEN_PY%"
if not exist "%LUMEN_VENV%\Scripts\python.exe" py -%LUMEN_PY% -m venv "%LUMEN_VENV%" || exit /b 1
set "LUMEN_EXE=%LUMEN_VENV%\Scripts\python.exe"
exit /b 0
