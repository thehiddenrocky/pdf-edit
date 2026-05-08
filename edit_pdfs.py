import os
import glob
import fitz

def main():
    current_dir = os.getcwd()
    original_dir = os.path.join(current_dir, "original")
    new_dir = os.path.join(current_dir, "new")
    
    # Create original and new folders
    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(new_dir, exist_ok=True)
    
    print(f"Scanning for .pdf files in: {current_dir}")
    
    # Find all .pdf files in this folder
    pdf_files = [f for f in glob.glob(os.path.join(current_dir, "*.pdf")) if os.path.isfile(f)]
    
    if not pdf_files:
        print("No .pdf files found in the current directory.")
        return
        
    for file_path in pdf_files:
        filename = os.path.basename(file_path)
        print(f"\nProcessing: {filename} ...")
        
        # Move the original file to the 'original' folder
        original_path = os.path.join(original_dir, filename)
        os.rename(file_path, original_path)
        
        try:
            doc = fitz.open(original_path)
            for page in doc:
                replacements = [] # List of (rect, text)
                redacted_areas = []

                # Redact and Replace function
                def process_rect(rect, new_text=None, wipe_x1=None):
                    # wipe_x1 allows us to extend the redaction to the right
                    rx1 = wipe_x1 if wipe_x1 else rect.x1
                    redact_rect = fitz.Rect(rect.x0, rect.y0, rx1, rect.y1)
                        
                    page.add_redact_annot(redact_rect, fill=(1, 1, 1))
                    redacted_areas.append(redact_rect)
                    
                    if new_text:
                        replacements.append((rect, new_text))

                # --- 1. Top Section (Sender Name & Address) ---
                # Find the exact title bounding box (usually top left)
                for inst in page.search_for("HIMANSHU RAJ"):
                    if inst.y0 < 300: # Ensure it's the top header
                        process_rect(inst, "MARY GARG", wipe_x1=inst.x1 + 50)
                    
                for inst in page.search_for("E-56, Saket, South Delhi"):
                    process_rect(inst, "vernerintie 6a", wipe_x1=inst.x1 + 50)
                for inst in page.search_for("Delhi-110017"):
                    process_rect(inst, "02430 finland", wipe_x1=inst.x1 + 50)

                # --- 2. Invoice Details Section ---
                for inst in page.search_for("Invoice Date:"):
                    date_rect = fitz.Rect(inst.x1 + 2, inst.y0, inst.x1 + 100, inst.y1)
                    process_rect(date_rect, "30/04/2026")

                # --- 3. Table Adjustments ---
                for inst in page.search_for("28"):
                    if 350 < inst.x0 < 450: # Hrs column
                        process_rect(inst, "13.33")
                for inst in page.search_for("€420.00"):
                    process_rect(inst, "€200.00")

                # --- 4. Payment Details Section (This is where the bug was) ---
                # First, find exactly where "Account Name:" is.
                acc_name_rects = page.search_for("Account Name:")
                for inst in acc_name_rects:
                    # Wipe the ENTIRE line starting from "Account Name:" to the edge of the page
                    wide_rect = fitz.Rect(inst.x0, inst.y0 - 2, page.rect.width, inst.y1 + 2)
                    process_rect(wide_rect, "Account Name: RIVERA MARY GARG")
                    
                # Do the same for Account Number
                acc_num_rects = page.search_for("Account Number:")
                for inst in acc_num_rects:
                    wide_rect = fitz.Rect(inst.x0, inst.y0 - 2, page.rect.width, inst.y1 + 2)
                    process_rect(wide_rect, "Account Number: FI71 1432 3500 3648 49")
                    
                # Completely wipe IFSC Code
                ifsc_rects = page.search_for("IFSC Code:")
                for inst in ifsc_rects:
                    wide_rect = fitz.Rect(inst.x0, inst.y0 - 2, page.rect.width, inst.y1 + 2)
                    process_rect(wide_rect, None) # No replacement text

                # --- 5. Bottom Section (Signature) ---
                for inst in page.search_for("Himanshu Raj"):
                    if inst.y0 > 750: # The signature is around y=767
                        process_rect(inst, "Mary Garg", wipe_x1=inst.x1 + 50)

                # Apply Redactions
                if redacted_areas:
                    page.apply_redactions()
                    
                # Apply Text Insertions
                for rect, text in replacements:
                    page.insert_text((rect.x0, rect.y1 - 2), text, fontsize=11, fontname="helv", color=(0, 0, 0))
            
            # Generate the new filename and save
            new_filename = filename.replace("Himanshu", "Mary_Garg")
            new_path = os.path.join(new_dir, new_filename)
            doc.save(new_path)
            print(f"✓ Successfully processed and saved to: new/{new_filename}")
        except Exception as e:
            print(f"✗ Failed to process {filename}: {e}")
            
    print("\nAll edits finished.")

if __name__ == "__main__":
    main()
