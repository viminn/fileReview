import re
import pdfplumber

file = "UnofficialTranscript.pdf"
fullOutput = 'output.txt'
justHonors = "honors.txt"
roughRE = "^([a-zA-Z]{3,4})\s*(\d{1,3})\s*(.*?)(HONORS.*|\n.*?HONORS.*)"
# not working step2 = "^[A-Z]{3} \d{3} Kutztown UG .+ HONORS [A-F][+-]? \d\.\d{3} \d{2}\.\d{2}$"

# Open the PDF file and extract text
with pdfplumber.open(file) as pdf:
    with open(fullOutput, 'w', encoding='utf-8') as text_file:
        for page in pdf.pages:
            text = page.extract_text()
            if text:  # Check if text was extracted
                text_file.write(text + '\n')  # Write the text to the file
