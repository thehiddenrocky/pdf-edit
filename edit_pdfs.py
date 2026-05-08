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
                replacements = []
                redact_only = []
                
                # 1. Name & Address
                for inst in page.search_for("HIMANSHU RAJ"):
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                    replacements.append((inst, "MARY GARG"))
                
                # If they were separate (fallback)
                for inst in page.search_for("HIMANSHU"):
                    if not any(inst.intersects(r[0]) for r in replacements):
                        page.add_redact_annot(inst, fill=(1, 1, 1))
                        replacements.append((inst, "MARY GARG"))
                
                for inst in page.search_for("RAJ"):
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                for inst in page.search_for("Raj"):
                    page.add_redact_annot(inst, fill=(1, 1, 1))

                # Address lines
                for inst in page.search_for("E-56, Saket, South Delhi"):
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                    replacements.append((inst, "vernerintie 6a"))
                for inst in page.search_for("Delhi-110017"):
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                    replacements.append((inst, "02430 finland"))

                # 2. Invoice Date
                for inst in page.search_for("Invoice Date:"):
                    # Redact the part after "Invoice Date: "
                    rect = fitz.Rect(inst.x1, inst.y0, page.rect.width, inst.y1)
                    page.add_redact_annot(rect, fill=(1, 1, 1))
                    replacements.append((fitz.Rect(inst.x1 + 2, inst.y0, inst.x1 + 100, inst.y1), "30/04/2026"))

                # 3. Table Adjustments (Total €200)
                # Hours: 28 -> 13.33
                for inst in page.search_for("28"):
                    # Ensure we're in the Hrs column (approximate x location)
                    if 350 < inst.x0 < 450:
                        page.add_redact_annot(inst, fill=(1, 1, 1))
                        replacements.append((inst, "13.33"))

                # Amounts: €420.00 -> €200.00
                for inst in page.search_for("€420.00"):
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                    replacements.append((inst, "€200.00"))

                # 4. Account Details
                for inst in page.search_for("Account Name:"):
                    rect = fitz.Rect(inst.x0, inst.y0, page.rect.width, inst.y1)
                    page.add_redact_annot(rect, fill=(1, 1, 1))
                    replacements.append((inst, "Account Name: RIVERA MARY GARG"))

                for inst in page.search_for("Account Number:"):
                    rect = fitz.Rect(inst.x0, inst.y0, page.rect.width, inst.y1)
                    page.add_redact_annot(rect, fill=(1, 1, 1))
                    replacements.append((inst, "Account Number: FI71 1432 3500 3648 49"))

                for inst in page.search_for("IFSC Code:"):
                    rect = fitz.Rect(inst.x0, inst.y0, page.rect.width, inst.y1)
                    page.add_redact_annot(rect, fill=(1, 1, 1))

                # Final Name at bottom
                for inst in page.search_for("Himanshu Raj"):
                    if inst.y0 > 500: # Bottom signature area
                        page.add_redact_annot(inst, fill=(1, 1, 1))
                        replacements.append((inst, "Mary Garg"))

                if replacements:
                    page.apply_redactions()
                    for rect, text in replacements:
                        # Insert text at the rect's location
                        page.insert_text((rect.x0, rect.y1 - 2), text, fontsize=10, fontname="helv", color=(0, 0, 0))
            
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
