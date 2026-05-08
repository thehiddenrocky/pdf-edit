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
                
                # 1. Replace HIMANSHU with MARY GARG
                for inst in page.search_for("HIMANSHU"):
                    replacements.append((inst, "MARY GARG"))
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                    
                # 2. Replace Himanshu with Mary Garg
                for inst in page.search_for("Himanshu"):
                    if not any(abs(inst.x0 - r[0].x0) < 1 and abs(inst.y0 - r[0].y0) < 1 for r in replacements):
                        replacements.append((inst, "Mary Garg"))
                        page.add_redact_annot(inst, fill=(1, 1, 1))

                # 3. Remove RAJ
                for inst in page.search_for("RAJ"):
                    redact_only.append(inst)
                    page.add_redact_annot(inst, fill=(1, 1, 1))
                for inst in page.search_for("Raj"):
                    redact_only.append(inst)
                    page.add_redact_annot(inst, fill=(1, 1, 1))

                # 4. Update Account Name to RIVERA MARY
                # Note: "Account Name: Himanshu Raj" will become "Account Name: Mary Garg" 
                # from the previous steps. So we search for "Mary Garg" on the Account Name line 
                # or just look for "Account Name:" and replace the whole thing.
                # It's cleaner to just redact the whole line and rewrite it.
                for inst in page.search_for("Account Name:"):
                    # Find the bounding box for the entire line
                    rect = fitz.Rect(inst.x0, inst.y0, page.rect.width, inst.y1)
                    redact_only.append(rect)
                    page.add_redact_annot(rect, fill=(1, 1, 1))
                    replacements.append((inst, "Account Name: RIVERA MARY"))

                # 5. Update Account Number
                for inst in page.search_for("Account Number:"):
                    rect = fitz.Rect(inst.x0, inst.y0, page.rect.width, inst.y1)
                    redact_only.append(rect)
                    page.add_redact_annot(rect, fill=(1, 1, 1))
                    replacements.append((inst, "Account Number: FI71 1432 3500 3648 49"))

                # 6. Remove IFSC Code
                for inst in page.search_for("IFSC Code:"):
                    rect = fitz.Rect(inst.x0, inst.y0, page.rect.width, inst.y1)
                    redact_only.append(rect)
                    page.add_redact_annot(rect, fill=(1, 1, 1))

                if replacements or redact_only:
                    page.apply_redactions()
                    for inst, text in replacements:
                        # Insert new text, positioning slightly above the bottom of the bounding box
                        page.insert_text((inst.x0, inst.y1 - 2), text, fontsize=11, fontname="helv", color=(0, 0, 0))
            
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
