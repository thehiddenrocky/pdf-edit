import fitz
doc = fitz.open()
page = doc.new_page()

try:
    # Font names based on PyMuPDF documentation for base-14 fonts
    # Helvetica-Oblique is simply requested by its full name or "ho" if mapped internally
    page.insert_text((50, 100), "Hello Italic", fontname="Helvetica-Oblique")
    print("Helvetica-Oblique worked")
except Exception as e:
    print("Helvetica-Oblique failed:", e)
