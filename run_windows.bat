@echo off
setlocal
cd /d "%~dp0"
call select_python.bat %1 || goto fail
"%LUMEN_EXE%" -m pip install -r requirements-windows.txt || goto fail
"%LUMEN_EXE%" lumen_win.py
exit /b %errorlevel%
:fail
pause
exit /b 1
