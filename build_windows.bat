@echo off
setlocal
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --onefile --name PDF-Flatten-Tool --icon app.ico app.py
if %errorlevel% neq 0 (
  echo Build failed.
  pause
  exit /b %errorlevel%
)
echo.
echo Build complete. Your EXE is in the dist folder:
echo dist\PDF-Flatten-Tool.exe
pause
