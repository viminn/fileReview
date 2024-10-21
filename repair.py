#!/usr/bin/env python
# coding: utf-8

import re
import pdfplumber
from pprint import pprint
import json

file = "bigUnofficiaTranscript.pdf"
text = ""

honorsRE = re.compile(r'.*honors', re.IGNORECASE)
courseRE = re.compile(r'[A-Z]+\s\d{2,3}')
courseLineRE = re.compile(r'([A-Z]+ \d+) (\w+\s*\w*) ([UGA]*) (\D+?) ([ABCDF-]*)\s?(\d\.\d{3})')
nameRE = re.compile(r'^([A-Za-z]+), ([A-Za-z]+)')
studentChunkRE = re.compile('(Kutztown\nUnofficial Academic Transcript\n.*?)(?=Kutztown\nUnofficial Academic Transcript\n)|(Kutztown\nUnofficial Academic Transcript\n.*)$', re.DOTALL)

# put all text of a pdf into a string
with pdfplumber.open(file) as pdf:
    for page in pdf.pages:
        text += page.extract_text() + "\n"
# print(text)
# split the string across students
allStudentList = re.split(studentChunkRE,text)
allStudentList = filter(None, allStudentList)

allStudentList = list(filter(len,allStudentList))
# print(allStudentList[4])
# print(len(allStudentList))

studentJSON = {}

for student in allStudentList:
    courseList = []
    joinedCourseList = []
    honorsList = []
    studentName = ""
    courseDict = {}
    
    # build a list of all a student's courses
    for line in student.split('\n'):
        if honorsRE.match(line) or courseRE.match(line):
            courseList.append(line)
        if nameRE.match(line):
            line = nameRE.search(line)
            if line:
                lastName = line.group(1)
                firstName = line.group(2)
                studentName = firstName + ' ' + lastName
    
    # join lines where Campus HONORS is on the next line
    for entry in courseList:
        if entry == 'Campus HONORS':
            if joinedCourseList:
                joinedCourseList[-1] += ' ' + entry
        else:
            joinedCourseList.append(entry)

    # build a list of honors courses
    for course in joinedCourseList:
        if honorsRE.match(course):
            honorsList.append(course)

    cleanedHonorsList = [s.replace('\n', '') for s in honorsList]
    
    # parse out a course into pieces of info
    for course in cleanedHonorsList:
        if courseLineRE.match(course):
            course = courseLineRE.search(course)
            if course:
                courseCode = course.group(1)
                title = course.group(4)
                grade = course.group(5)
                creditHours = course.group(6)
                courseDict[courseCode] = {"title": title, "grade": grade, "credits": creditHours}
    studentJSON[studentName] = courseDict

pprint(studentJSON)





