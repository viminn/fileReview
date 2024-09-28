import re
from pdfminer.high_level import extract_pages, extract_text

text = extract_text("Unofficial Transcript.pdf")
print(text)
# for page_layout in extract_pages("SSR.pdf"):
#     for element in page_layout:
#         print(element)