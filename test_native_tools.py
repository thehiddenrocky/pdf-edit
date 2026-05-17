import os
import fitz
from tools import merge_pdfs, split_pdf, rotate_pdf_pages, remove_pdf_pages, replace_text_in_pdf, ocr_pdf

def create_test_pdf(filename, text, pages=1):

    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((50, 50), f"{text} - Page {i+1}")
    doc.save(filename)
    doc.close()
    return filename

def test_tools():
    # 1. Create dummy PDFs
    f1 = create_test_pdf("test1.pdf", "File One with some unique text", pages=2)
    f2 = create_test_pdf("test2.pdf", "File Two", pages=1)
    
    print("--- Testing Replace Text ---")
    res_replace = replace_text_in_pdf("test1.pdf", "unique text", "NEW TEXT")
    print(res_replace)
    if "Success" in res_replace:
        doc = fitz.open("new/test1.pdf")
        text = doc[0].get_text()
        print(f"Text check: {'NEW TEXT' in text} (Expected: True)")
        doc.close()

    print("\n--- Testing Merge ---")
    res_merge = merge_pdfs([f1, f2], "merged.pdf")
    print(res_merge)
    if "Success" in res_merge:
        doc = fitz.open("new/merged.pdf")
        print(f"Merged page count: {doc.page_count} (Expected: 3)")
        doc.close()

    print("\n--- Testing Split ---")
    res_split = split_pdf("new/merged.pdf", "1, 3")
    print(res_split)
    if "Success" in res_split:
        doc = fitz.open("new/split_merged.pdf")
        print(f"Split page count: {doc.page_count} (Expected: 2)")
        doc.close()

    print("\n--- Testing Rotate ---")
    res_rotate = rotate_pdf_pages("test1.pdf", "1", 90)
    print(res_rotate)
    if "Success" in res_rotate:
        doc = fitz.open("new/test1.pdf")
        print(f"Page 1 rotation: {doc[0].rotation} (Expected: 90)")
        doc.close()

    print("\n--- Testing Remove ---")
    res_remove = remove_pdf_pages("test1.pdf", "2")
    print(res_remove)
    if "Success" in res_remove:
        doc = fitz.open("new/test1.pdf")
        print(f"Page count after removal: {doc.page_count} (Expected: 1)")
        doc.close()

    print("\n--- Testing OCR ---")
    res_ocr = ocr_pdf("test2.pdf")
    print(res_ocr)

    # Cleanup
    for f in ["test1.pdf", "test2.pdf", "new/merged.pdf", "new/split_merged.pdf", "new/test1.pdf", "new/ocr_test2.pdf"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass
    if os.path.exists("new") and not os.listdir("new"):
        try:
            os.rmdir("new")
        except Exception:
            pass

if __name__ == "__main__":
    test_tools()
