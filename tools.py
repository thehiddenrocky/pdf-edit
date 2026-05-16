import fitz  # PyMuPDF
import json
import os
import re

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
        if not os.path.exists(filepath):
            return f"Error: File not found at {filepath}"
            
        doc = fitz.open(filepath)
        changes_made = 0
        
        for page in doc:
            instances = page.search_for(old_text)
            if not instances:
                continue
                
            for inst in instances:
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
            # Save to the 'new' directory relative to the file
            base_dir = os.path.dirname(filepath)
            if os.path.basename(base_dir) == "new":
                new_dir = base_dir
            else:
                new_dir = os.path.join(base_dir, "new")
            os.makedirs(new_dir, exist_ok=True)
            filename = os.path.basename(filepath)
            new_filepath = os.path.normpath(os.path.join(new_dir, filename))
            
            doc.save(new_filepath)
            doc.close()
            return f"Success: Replaced '{old_text}' with '{new_text}' {changes_made} times. Saved to {new_filepath}"
        else:
            doc.close()
            return f"No occurrences of '{old_text}' found in the document."
            
    except Exception as e:
        return f"Error replacing text in PDF: {str(e)}"

def _parse_page_ranges(range_str: str, max_pages: int) -> list[int]:
    """Parses strings like '1-3, 5, 7-10' into a list of 0-based page indices."""
    pages = []
    parts = [p.strip() for p in range_str.split(",")]
    for part in parts:
        if "-" in part:
            start, end = part.split("-")
            # Convert 1-based to 0-based
            s = int(start) - 1
            e = int(end)
            pages.extend(range(s, min(e, max_pages)))
        else:
            pages.append(int(part) - 1)
    # Remove duplicates and sort, ensuring within bounds
    return sorted(list(set([p for p in pages if 0 <= p < max_pages])))

def merge_pdfs(filepaths: list[str], output_filename: str) -> str:
    """Merges multiple PDF files into a single PDF.
    
    Args:
        filepaths: List of paths to PDF files to merge.
        output_filename: Name for the resulting merged PDF.
    """
    try:
        result_doc = fitz.open()
        for path in filepaths:
            if not os.path.exists(path):
                return f"Error: File not found at {path}"
            src_doc = fitz.open(path)
            result_doc.insert_pdf(src_doc)
            src_doc.close()
            
        base_dir = os.path.dirname(filepaths[0])
        if os.path.basename(base_dir) == "new":
            new_dir = base_dir
        else:
            new_dir = os.path.join(base_dir, "new")
        os.makedirs(new_dir, exist_ok=True)
        output_path = os.path.join(new_dir, output_filename)
        
        result_doc.save(output_path)
        result_doc.close()
        return f"Success: Merged {len(filepaths)} files into {output_path}"
    except Exception as e:
        return f"Error merging PDFs: {str(e)}"

def split_pdf(filepath: str, page_ranges: str) -> str:
    """Splits a PDF by extracting specific page ranges into a new file.
    
    Args:
        filepath: Path to the PDF file.
        page_ranges: String representing page ranges (e.g., '1-3, 5, 8-10').
    """
    try:
        if not os.path.exists(filepath):
            return f"Error: File not found at {filepath}"
            
        doc = fitz.open(filepath)
        page_indices = _parse_page_ranges(page_ranges, doc.page_count)
        
        if not page_indices:
            return f"Error: Invalid page ranges '{page_ranges}' for file with {doc.page_count} pages."
            
        # Select keeps only the specified pages in the current document
        doc.select(page_indices)
        
        base_dir = os.path.dirname(filepath)
        if os.path.basename(base_dir) == "new":
            new_dir = base_dir
        else:
            new_dir = os.path.join(base_dir, "new")
            
        os.makedirs(new_dir, exist_ok=True)
        filename = f"split_{os.path.basename(filepath)}"
        output_path = os.path.join(new_dir, filename)
        
        doc.save(output_path)
        doc.close()
        
        return f"Success: Extracted pages {page_ranges} to {output_path}"
    except Exception as e:
        return f"Error splitting PDF: {str(e)}"

def rotate_pdf_pages(filepath: str, page_ranges: str, rotation: int) -> str:
    """Rotates specific pages in a PDF.
    
    Args:
        filepath: Path to the PDF file.
        page_ranges: String representing page ranges (e.g., '1-3, 5'). Use 'all' for all pages.
        rotation: Degrees to rotate (must be a multiple of 90, e.g., 90, 180, 270).
    """
    try:
        if not os.path.exists(filepath):
            return f"Error: File not found at {filepath}"
            
        if rotation % 90 != 0:
            return "Error: Rotation must be a multiple of 90 degrees."
            
        doc = fitz.open(filepath)
        if page_ranges.lower() == 'all':
            page_indices = list(range(doc.page_count))
        else:
            page_indices = _parse_page_ranges(page_ranges, doc.page_count)
            
        for idx in page_indices:
            page = doc[idx]
            current_rot = page.rotation
            page.set_rotation((current_rot + rotation) % 360)
            
        base_dir = os.path.dirname(filepath)
        if os.path.basename(base_dir) == "new":
            new_dir = base_dir
        else:
            new_dir = os.path.join(base_dir, "new")
        os.makedirs(new_dir, exist_ok=True)
        output_path = os.path.join(new_dir, os.path.basename(filepath))
        
        doc.save(output_path)
        doc.close()
        
        return f"Success: Rotated pages {page_ranges} by {rotation} degrees. Saved to {output_path}"
    except Exception as e:
        return f"Error rotating PDF pages: {str(e)}"

def remove_pdf_pages(filepath: str, page_ranges: str) -> str:
    """Removes specific pages from a PDF.
    
    Args:
        filepath: Path to the PDF file.
        page_ranges: String representing page ranges to REMOVE (e.g., '2, 4-6').
    """
    try:
        if not os.path.exists(filepath):
            return f"Error: File not found at {filepath}"
            
        doc = fitz.open(filepath)
        page_indices = _parse_page_ranges(page_ranges, doc.page_count)
        
        if not page_indices:
            return f"Error: Invalid page ranges '{page_ranges}'."
            
        # We need to delete from end to start to avoid index shifts
        for idx in reversed(page_indices):
            doc.delete_page(idx)
            
        base_dir = os.path.dirname(filepath)
        if os.path.basename(base_dir) == "new":
            new_dir = base_dir
        else:
            new_dir = os.path.join(base_dir, "new")
        os.makedirs(new_dir, exist_ok=True)
        output_path = os.path.join(new_dir, os.path.basename(filepath))
        
        doc.save(output_path)
        doc.close()
        
        return f"Success: Removed pages {page_ranges}. Saved to {output_path}"
    except Exception as e:
        return f"Error removing PDF pages: {str(e)}"

def apply_pdf_edits(filepath: str, edit_instructions: str) -> str:
    """DEPRECATED: Use granular tools (merge, split, rotate, remove) instead.
    Formerly used Stirling-PDF backend. Now returns a message suggesting specific tools.
    """
    return (
        "Error: 'apply_pdf_edits' is deprecated and Stirling-PDF is no longer supported. "
        "Please use granular tools like 'merge_pdfs', 'split_pdf', 'rotate_pdf_pages', or 'remove_pdf_pages' instead."
    )
