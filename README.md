# Sprint Files - PDF Tools

This folder contains scripts for converting DOCX files to PDF and performing specific edits on PDF resumes.

## Prerequisites

- **macOS**: These scripts utilize AppleScript and Microsoft Word for high-fidelity conversion.
- **Microsoft Word**: Must be installed for `docx2pdf` to function.
- **Python 3.14+**: The environment used during development.

## Setup Instructions

1. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install required libraries**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Convert all DOCX to PDF
Run the conversion script to turn all `.docx` files in this directory into PDFs:
```bash
python venv/scripts/convert.py
```

### 2. Update CV (Mayank CV 2026)
To apply the specific date changes to Mayank's CV:
```bash
python venv/scripts/modify_pdf.py
```

## Troubleshooting

- **Permissions**: If macOS blocks AppleScript execution, you may need to grant "Accessibility" or "Automation" permissions to your Terminal/IDE in `System Settings > Privacy & Security`.
- **Word Dialogs**: Ensure Microsoft Word is not stuck on a "Welcome" or "Update" dialog, as this will block the background conversion process.
