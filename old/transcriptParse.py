# with open("~/Downloads/transcriptNoLayout.txt", "r") as transcript:
    # content = transcript.readlines()
    # print(content)
    # print(transcript.readlines)
import re
from pdfminer.high_level import extract_pages, extract_text

with open("dumpText.txt", 'w') as file:
    text = extract_text("Unofficial Transcript.pdf")
    file.write(text)
with open('dumpText.txt', 'r') as file:
    # content = file.read()
    # print(content)
    with open('joined.txt', 'w') as output:
        for line in file:
        # Use regex to remove all numbers from the line
            line_without_numbers = re.sub(r'\d+', '', line)
            if line_without_numbers.strip() != '':
                if line_without_numbers != ".\n":
                    output.write(line_without_numbers)