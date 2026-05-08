import fitz
doc = fitz.open("original/20 Feb-Himanshu.pdf")
page = doc[0]

# Find images on the page
image_list = page.get_images(full=True)
print(f"Found {len(image_list)} images on page 0")

for img_index, img in enumerate(image_list):
    xref = img[0]
    bbox = page.get_image_bbox(img)
    print(f"Image {img_index}: xref={xref}, bbox={bbox}")
