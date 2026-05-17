# PDF Edit - Automated Invoice Tool

A Python-based utility and AI Agent to programmatically update PDF invoices, handling text replacement, financial calculations, and signature image swapping with high precision.

## 🚀 New: PDF AI Agent
The project now includes an LLM-powered agent that can interpret natural language instructions to edit PDFs.

### Usage
```bash
source venv/bin/activate
python main.py "change the date to 15 August 2026" "original/invoice.pdf"
```
For detailed implementation notes, troubleshooting, and advanced usage, see the [**PDF Agent Guide**](docs/AGENT_GUIDE.md).

## Prerequisites
- **Python 3.10+**
- **Ollama**: Required for running local LLMs (e.g., Gemma 2).
- **Google Gemini API Key**: Optional (if using Gemini instead of local models).
- **Tesseract-OCR**: Optional (required only for the `ocr_pdf` tool). On macOS: `brew install tesseract`.

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

### 1. Process Invoices
Place the source PDF in the root directory and run:
```bash
python edit_pdfs.py
```
- Original files are moved to `original/`.
- Edited files are saved in `new/`.

### 2. Debugging Tools
- `python debug_rects.py`: Visualizes bounding boxes for all text to help with targeting.
- `python debug_images.py`: Identifies image `xref` IDs and positions.
- `python font_test.py`: Verifies if specific PDF fonts (like italics) are rendering correctly.

## Methodology & Learnings

### 1. The Redaction Workflow
PyMuPDF requires a two-step process to "edit" PDFs:
1. **Marking**: Use `page.add_redact_annot(rect, fill=(1,1,1))` to draw white rectangles over old content.
2. **Applying**: Call `page.apply_redactions()` once per page.
3. **Inserting**: Use `page.insert_text()` *after* applying redactions to ensure the new text is rendered on top of the clean background.

### 2. Coordinate-Based Targeting
When a string (like a name) appears in multiple places (Header and Signature), simple text search isn't enough.
- **Vertical Filtering**: Use `y0` coordinates to distinguish sections (e.g., Header < 300px, Body 300-750px, Signature > 750px).
- **Horizontal Filtering**: Target specific columns (like the 'Hrs' column) by restricting the `x0` range.

### 3. Native Font Handling
To avoid "font file not found" errors, use the **Base-14 PDF fonts** natively understood by PyMuPDF.
- Use `fontname="helv"` for standard text.
- Use `fontname="Helvetica-Oblique"` for italicized signatures.
- No external `.ttf` or `.otf` files are required for these standard faces.

### 4. Relative Image Placement
To replace an image signature dynamically:
1. Search for the text signature marker (e.g., "Mary Garg").
2. Calculate a rectangle relative to that text (e.g., `y0 - 80` to `y0 - 5`).
3. Apply a redaction to clear the old image.
4. Insert the new image (`page.insert_image()`) into that relative box, adjusting for aspect ratio if necessary.
