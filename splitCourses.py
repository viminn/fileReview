#!/usr/bin/env python
# coding: utf-8
import re
import pdfplumber
from pprint import pprint
import json

file = "UnofficialTranscript.pdf"
text = ""

with pdfplumber.open(file) as pdf:
    for page in pdf.pages:
        text += page.extract_text()
honorsRE = re.compile(r'.*honors', re.IGNORECASE)
courseRE = re.compile(r'[A-Z]+\s\d{2,3}')
courseList = []
for line in text.split('\n'):
    if honorsRE.match(line) or courseRE.match(line):
        courseList.append(line)
# pprint(courseList)

newList = []
for entry in courseList:
    if entry == 'Campus HONORS':
        if newList:
            newList[-1] += ' ' + entry
    else:
        newList.append(entry)
# pprint(newList)

honorsList = []
for course in newList:
    if honorsRE.match(course):
        honorsList.append(course)
cleaned = [s.replace('\n', '') for s in honorsList]

# print(cleaned)
pprint(honorsList)
courseJSON = []
courseLineRE = re.compile(r'([A-Z]+ \d+) (\w+\s*\w*) ([UGA]*) (\D+?) ([ABCDF-]*)\s?(\d\.\d{3})')
for course in cleaned:
    if courseLineRE.match(course):
        course = courseLineRE.search(course)
        if course:
            courseCode = course.group(1)
            title = course.group(4)
            grade = course.group(5)
            creditHours = course.group(6)
            courseDict = {courseCode: {"title": title, "grade": grade, "credits": creditHours}}
            courseJSON.append(courseDict)

nameRE = re.compile(r'^([A-Za-z]+), ([A-Za-z]+)')
for line in text.split('\n'):
    if nameRE.match(line):
        line = nameRE.search(line)
        if line:
            lastName = line.group(1)
            firstName = line.group(2)
            studentJSON = {firstName + ' ' + lastName: courseJSON}
# pprint(studentJSON)
y = json.dumps(studentJSON)
pprint(studentJSON)
