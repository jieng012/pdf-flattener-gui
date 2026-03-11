# PDF Flatten Tool

A small desktop app with a GUI to import an existing PDF, strongly flatten it, and export a harder-to-edit PDF.

## Languages
- Chinese (中文)
- English
- Bahasa Melayu

## What this tool does
This app uses **strong image-based flattening**:
1. Open the source PDF.
2. Render each page into a high-resolution image.
3. Rebuild a new PDF page by page.
4. Export the new flattened PDF.

This makes the output PDF much harder to edit visually. In exchange, searchable text, copyable text, form fields, links, layers, and most interactive PDF features are usually lost.

## Recommended settings
- 150 DPI: smaller file size
- 200 DPI: recommended balance
- 300 DPI: clearer, but larger file size

## Run locally
```bash
pip install -r requirements.txt
python app.py
```

## CLI mode
```bash
python app.py --cli --input input.pdf --output output.pdf --dpi 200 --lang en
```

## Build a Windows EXE
Run the included script on a **Windows** machine:
```bat
build_windows.bat
```

Or manually:
```bat
python -m pip install -r requirements.txt
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --onefile --name PDF-Flatten-Tool --icon app.ico app.py
```

## Build on Linux
```bash
./build_linux.sh
```

## Notes
- Password-protected PDFs are not supported in this version.
- The output path must be different from the source path.
- For very large PDFs, 150 or 200 DPI is recommended first.
