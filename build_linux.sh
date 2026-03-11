#!/usr/bin/env bash
set -e
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --onefile --name pdf-flatten-tool app.py
printf '\nBuild complete. Binary: dist/pdf-flatten-tool\n'
