import fitz
doc = fitz.open()
page = doc.new_page()

try:
    page.insert_text((50, 50), "Hello Normal", fontname="helv")
    print("Normal worked")
except Exception as e:
    print("Normal failed:", e)

try:
    page.insert_font(fontname="F1", fontfile=None, fontbuffer=None, set_simple=False, encoding=0, basefont="Helvetica-Oblique")
    page.insert_text((50, 100), "Hello Italic", fontname="F1")
    print("Basefont worked")
except Exception as e:
    print("Basefont failed:", e)
