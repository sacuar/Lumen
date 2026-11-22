@echo off
setlocal
cd /d "%~dp0"
call select_python.bat %1 || goto fail
"%LUMEN_EXE%" -m pip install -r requirements-windows.txt || goto fail
"%LUMEN_EXE%" tools\build_brand.py || goto fail
"%LUMEN_EXE%" -m unittest discover -s tests -v || goto fail
"%LUMEN_EXE%" -m PyInstaller --clean --noconfirm Lumen.spec || goto fail
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
 echo Install Inno Setup 6 from https://jrsoftware.org/isdl.php
 goto fail
)
for /f "delims=" %%V in ('"%LUMEN_EXE%" -c "from lumen import __version__;print(__version__)"') do set "VER=%%V"
"%ISCC%" /DAppVersion=%VER% packaging\windows\Lumen.iss || goto fail
echo Installer: installer\Lumen-%VER%-Setup-x64.exe
pause
exit /b 0
:fail
echo Build failed.
pause
exit /b 1
