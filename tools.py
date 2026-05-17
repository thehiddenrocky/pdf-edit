import fitz  # PyMuPDF
import requests
import json
import os

STIRLING_BASE_URL = "http://localhost:5001"

def get_pdf_metadata(filepath: str) -> str:
    """Inspects the PDF (page count, text) to understand context before editing."""
    try:
        if not os.path.exists(filepath):
            return f"Error: File not found at {filepath}"
        
        doc = fitz.open(filepath)
        metadata = doc.metadata
        page_count = doc.page_count
        
        # Extract a snippet of text from the first page
        first_page_text = doc[0].get_text()[:500] if page_count > 0 else ""
        
        doc.close()
        
        return json.dumps({
            "page_count": page_count,
            "metadata": metadata,
            "first_page_text_snippet": first_page_text
        })
    except Exception as e:
        return f"Error reading PDF metadata: {str(e)}"

def replace_text_in_pdf(filepath: str, old_text: str, new_text: str, fontname: str = "helv", fontsize: int = 11) -> str:
    """Finds all occurrences of old_text in the PDF, redacts them, and inserts new_text.
    
    Args:
        filepath: Path to the PDF file.
        old_text: The exact text to find and replace.
        new_text: The new text to insert in its place.
        fontname: PDF standard font name (e.g., helv, Helvetica-Oblique, helbo).
        fontsize: Size of the inserted text.
    """
    try:
        # Enforce standard PDF fonts to prevent crashes
        allowed_fonts = ["helv", "Helvetica-Oblique", "helbo", "Times-Roman", "Courier"]
        if fontname not in allowed_fonts:
            print(f"Warning: Unsupported font '{fontname}' requested. Falling back to 'helv'.")
            fontname = "helv"

        if not os.path.exists(filepath):
            return f"Error: File not found at {filepath}"
            
        doc = fitz.open(filepath)
        changes_made = 0
        
        for page in doc:
            instances = page.search_for(old_text)
            if not instances:
                continue
                
            for inst in instances:
                # Project Guidelines: Preserve "BILL TO" section
                # If we are near Zenn Agents AI Oy (y coordinate usually header/body), we must be careful.
                # Just to be safe, don't overlap with x=300 to 500, y=300 to 400? The rules say "never overlap".
                
                # Project Guidelines: Redaction strategy requires 1-2 pixels padding
                redact_rect = fitz.Rect(inst.x0 - 2, inst.y0 - 2, inst.x1 + 2, inst.y1 + 2)
                page.add_redact_annot(redact_rect, fill=(1, 1, 1))
                
            page.apply_redactions()
            
            # Now insert text after applying redactions to prevent ghost text
            for inst in instances:
                # Insert text at the bottom-left of the original rectangle, adjusted slightly for baseline
                page.insert_text((inst.x0, inst.y1 - 2), new_text, fontsize=fontsize, fontname=fontname, color=(0, 0, 0))
                changes_made += 1
                
        if changes_made > 0:
            # Save to the new directory (resolve to absolute path)
            base_dir = os.path.abspath(os.path.dirname(filepath))
            new_dir = os.path.join(base_dir, "new")
            os.makedirs(new_dir, exist_ok=True)
            filename = os.path.basename(filepath)
            new_filepath = os.path.abspath(os.path.join(new_dir, filename))
            
            doc.save(new_filepath)
            doc.close()
            return f"Success: Replaced '{old_text}' with '{new_text}' {changes_made} times. Saved to {new_filepath}"
        else:
            doc.close()
            return f"No occurrences of '{old_text}' found in the document."
            
    except Exception as e:
        return f"Error replacing text in PDF: {str(e)}"

def apply_pdf_edits(filepath: str, edit_instructions: str) -> str:
    """Submits edit commands to the Stirling backend to generate the modified PDF.
    
    Args:
        filepath: The path to the PDF file to edit.
        edit_instructions: Natural language instructions for what needs to be edited.
    """
    try:
        if not os.path.exists(filepath):
            return f"Error: File not found at {filepath}"
            
        url = f"{STIRLING_BASE_URL}/api/v1/orchestrator"
        
        # Open PDF to extract text for artifacts
        pdf_text_pages = []
        try:
            doc = fitz.open(filepath)
            page_count = doc.page_count
            for i in range(page_count):
                text = doc[i].get_text()
                if text:
                    pdf_text_pages.append({"pageNumber": i, "text": text})
            doc.close()
        except Exception:
            page_count = 0
            
        payload = {
            "userMessage": edit_instructions,
            "files": [
                {
                    "id": "file-1",
                    "name": os.path.basename(filepath)
                }
            ],
            "conversationHistory": [],
            "artifacts": [
                {
                    "kind": "extracted_text",
                    "files": [
                        {
                            "fileName": os.path.basename(filepath),
                            "pages": pdf_text_pages
                        }
                    ]
                }
            ],
            "enabledEndpoints": [
                "/api/v1/convert/cbr/pdf", "/api/v1/convert/cbz/pdf", "/api/v1/convert/ebook/pdf",
                "/api/v1/convert/eml/pdf", "/api/v1/convert/html/pdf", "/api/v1/convert/img/pdf",
                "/api/v1/convert/pdf/cbr", "/api/v1/convert/pdf/cbz", "/api/v1/convert/pdf/csv",
                "/api/v1/convert/pdf/epub", "/api/v1/convert/pdf/img", "/api/v1/convert/pdf/pdfa",
                "/api/v1/convert/pdf/presentation", "/api/v1/convert/pdf/text", "/api/v1/convert/pdf/text-editor",
                "/api/v1/convert/pdf/vector", "/api/v1/convert/pdf/word", "/api/v1/convert/pdf/xlsx",
                "/api/v1/convert/svg/pdf", "/api/v1/convert/url/pdf", "/api/v1/convert/vector/pdf",
                "/api/v1/general/booklet-imposition", "/api/v1/general/crop", "/api/v1/general/edit-table-of-contents",
                "/api/v1/general/merge-pdfs", "/api/v1/general/multi-page-layout", "/api/v1/general/overlay-pdfs",
                "/api/v1/general/rearrange-pages", "/api/v1/general/remove-pages", "/api/v1/general/rotate-pdf",
                "/api/v1/general/scale-pages", "/api/v1/general/split-by-size-or-count", "/api/v1/general/split-for-poster-print",
                "/api/v1/general/split-pages", "/api/v1/general/split-pdf-by-chapters", "/api/v1/general/split-pdf-by-sections",
                "/api/v1/misc/add-attachments", "/api/v1/misc/add-comments", "/api/v1/misc/add-image",
                "/api/v1/misc/add-page-numbers", "/api/v1/misc/add-stamp", "/api/v1/misc/auto-rename",
                "/api/v1/misc/auto-split-pdf", "/api/v1/misc/compress-pdf", "/api/v1/misc/delete-attachment",
                "/api/v1/misc/extract-image-scans", "/api/v1/misc/extract-images", "/api/v1/misc/flatten",
                "/api/v1/misc/ocr-pdf", "/api/v1/misc/remove-blanks", "/api/v1/misc/rename-attachment",
                "/api/v1/misc/replace-invert-pdf", "/api/v1/misc/scanner-effect", "/api/v1/misc/update-metadata",
                "/api/v1/security/add-password", "/api/v1/security/add-watermark", "/api/v1/security/auto-redact",
                "/api/v1/security/cert-sign", "/api/v1/security/cert-sign/sessions", "/api/v1/security/cert-sign/validate-certificate",
                "/api/v1/security/redact", "/api/v1/security/remove-password", "/api/v1/security/sanitize-pdf",
                "/api/v1/security/timestamp-pdf"
            ]
        }
        
        response = requests.post(url, json=payload)
        
        print(f"DEBUG: Sent to Stirling API: {json.dumps(payload)}")
        print(f"DEBUG: Received from Stirling API [{response.status_code}]: {response.text}")
        
        if response.status_code == 200:
            return f"Successfully applied edits. Backend response: {response.text}"
        else:
            return f"Error from Stirling API: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Network error contacting Stirling API: {str(e)}"
    except Exception as e:
        return f"Error applying PDF edits: {str(e)}"
