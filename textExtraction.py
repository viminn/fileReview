import pdfplumber

output = "bigTranscript.txt"
pdf = "bigUnofficialTranscript.pdf"
with open(output,'w') as textFile:
    with pdfplumber.open(pdf) as source:
        for page in source.pages:
            text = page.extract_text()
            textFile.write(text + '\n')