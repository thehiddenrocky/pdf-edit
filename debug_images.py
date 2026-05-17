import fitz
import sys
import os

# Use provided file or default to the resume
filename = sys.argv[1] if len(sys.argv) > 1 else "Akshenndra- Garg Resume 2025.pdf"

if not os.path.exists(filename):
    # Try looking in 'original' folder if it exists
    alt_path = os.path.join("original", filename)
    if os.path.exists(alt_path):
        filename = alt_path
    else:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

print(f"Inspecting images in: {filename}")
doc = fitz.open(filename)

for page_index in range(len(doc)):
    page = doc[page_index]
    image_list = page.get_images(full=True)
    print(f"\n--- Page {page_index} (Found {len(image_list)} images) ---")

    for img_index, img in enumerate(image_list):
        xref = img[0]
        try:
            bbox = page.get_image_bbox(img)
            print(f"  Image {img_index}: xref={xref}, bbox={bbox}")
        except Exception:
            print(f"  Image {img_index}: xref={xref}, (could not determine bbox)")

doc.close()
