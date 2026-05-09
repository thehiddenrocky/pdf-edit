# PDF Edit - Automated Invoice/Resume Editor

This project provides a suite of Python scripts for automated editing of PDF documents, specifically tailored for updating invoice details.

## Project Guidelines & "Safe Zones"

### 1. Preservation of "BILL TO"
- The "BILL TO" section (typically "Zenn Agents AI Oy" and "Elannontie 3") must **NEVER** be modified. 
- Always ensure redaction rectangles do not overlap with these coordinates.

### 2. Strict Coordinate Targeting
- **Header Section (y < 300)**: Handle sender names and addresses here.
- **Body Section (300 < y < 750)**: Handle financial tables, hours, and totals.
- **Signature Section (y > 750)**: Handle bottom name text and image signatures.

## Technical Standards

### Redaction Strategy
- **DO NOT** try to insert text before applying redactions. This causes "ghost text" overlap.
- **Padding**: Always add 1-2 pixels of padding to redaction rectangles (`fitz.Rect(inst.x0-2, inst.y0-2, inst.x1+2, inst.y1+2)`) to ensure complete removal of original characters.

### Font Usage
- Use standard PDF font names:
  - `helv`: Helvetica (Regular)
  - `Helvetica-Oblique`: Helvetica (Italic)
  - `helbo`: Helvetica-Bold-Oblique
- Avoid referencing external `.ttf` files unless absolutely necessary for custom branding.

### Image Signatures
- The signature image (`mary-sign.jpg`) should be placed relative to the text signature.
- **Aspect Ratio**: The current logic uses a bounding box roughly `120x75` pixels. If the signature looks stretched, adjust the `y0` offset in `edit_pdfs.py`.

## Core Commands

- `python edit_pdfs.py`: Main processing script.
- `python debug_rects.py`: Use this first when the PDF layout changes to find new coordinates.
- `python debug_images.py`: Use this to verify if the old signature image `xref` has changed.

## Methodology History
We moved from simple text replacement to coordinate-aware redaction because the original PDFs often had complex layering. By "wiping" specific rectangular regions with white fill and then re-printing text at the exact same location, we maintain the original layout without artifacts.
