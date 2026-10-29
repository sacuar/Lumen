@echo off
setlocal

if not exist "lumen.ico" (
    echo WARNING: lumen.ico not found. The .exe will use PyInstaller's default icon.
    set ICON_FLAG=
) else (
    set ICON_FLAG=--icon "lumen.ico"
)

python -m pip install --upgrade pip
python -m pip install pywebview pyinstaller

pyinstaller --noconfirm --clean --windowed --name Lumen ^
  %ICON_FLAG% ^
  --add-data "lumen;lumen" ^
  --add-data "ui;ui" ^
  --add-data "sublime_shim;sublime_shim" ^
  --version-file version_info.txt ^
  lumen_win.py

echo.
echo Built: dist\Lumen\Lumen.exe
echo.
echo Next steps:
echo   1) Copy lumen.ico next to Lumen.exe if you haven't already
echo   2) Run:  python register_lumen.py "dist\Lumen\Lumen.exe"
echo   3) Right-click a .txt / .php / .html / .py file and pick
echo      "Open with" -^> "Choose another app" -^> Lumen -^> Always
echo.
pause