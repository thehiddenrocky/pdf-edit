import fitz
doc = fitz.open("20 Feb-Himanshu.pdf")
page = doc[0]

print("Matches for 'Himanshu':")
for r in page.search_for("Himanshu"):
    print(r)

print("\nMatches for 'Account Name:':")
for r in page.search_for("Account Name:"):
    print(r)
