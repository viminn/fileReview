import re
import pdfplumber
from pprint import pprint

# Your sample transcript string
text = """
Information Technology
Additional Standing
Dean's List
Subject Course Campus Level Title Grade Credit Quality R
Hours Points
ANT 212 Kutztown UG SHAMANS, WITCHES & MAGIC - A 3.000 12.00
Campus HONORS
CMP 200 Kutztown UG RESEARCH AND COMPOSITION - A 3.000 12.00
Campus HONORS
CSC 125 Kutztown UG Discrete Math for Computing I A 3.000 12.00
Campus
"""

split_courses = []
file = "UnofficialTranscript.pdf"
fullOutput = 'output.txt'
justHonors = "honors.txt"
roughRE = re.compile(r'^([a-zA-Z]{3,4})\s*(\d{1,3})\s*(.*?)(HONORS.*|\n.*?HONORS.*)')
with pdfplumber.open(file) as pdf:
    with open(fullOutput, 'w', encoding='utf-8') as text_file:
        for page in pdf.pages:
            text = page.extract_text()
            if text:  # Check if text was extracted
                text_file.write(text + '\n')  # Write the text to the file
                # split_courses += re.split(r'(?=[A-Z]{3,4} \d{1,3})', text)
                split_courses += re.split(r'(?=[A-Z]{3,4} \s*\d{1,3})', text)
                split_courses = [course.strip() for course in split_courses if course.strip()]
                # for course in split_courses:
                #     print(course)
        pprint(split_courses)
        #         entries = re.split('^[a-zA-Z]{3,4}\s*\d{1,3}', text)
        # print(entries)
    # with open(fullOutput, 'r') as textFile:
    #     for line in textFile:
    #         if roughRE.match(line):
    #             print(line)