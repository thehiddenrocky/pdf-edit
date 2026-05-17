import fitz
import sys
import os

# Use provided file or default to the resume
filename = sys.argv[1] if len(sys.argv) > 1 else "Akshenndra- Garg Resume 2025.pdf"

if not os.path.exists(filename):
    print(f"Error: File '{filename}' not found.")
    sys.exit(1)

doc = fitz.open(filename)
page = doc[0]

# Common things to search for
search_terms = ["Akshenndra", "Garg", "Education", "Experience"]

for term in search_terms:
    print(f"\nMatches for '{term}':")
    instances = page.search_for(term)
    if not instances:
        print("  None found.")
    for r in instances:
        print(f"  {r}")

doc.close()
