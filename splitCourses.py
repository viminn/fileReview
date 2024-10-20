import re
import pdfplumber
from pprint import pprint
import json

file = "UnofficialTranscript.pdf"
text = ""
courseList = []
newList = []
honorsList = []
courseJSON = []

honorsRE = re.compile(r'.*honors', re.IGNORECASE)
courseRE = re.compile(r'[A-Z]+\s\d{2,3}')
courseLineRE = re.compile(r'([A-Z]+ \d+) (\w+\s*\w*) ([UGA]*) (\D+?) ([ABCDF-]*)\s?(\d\.\d{3})')
nameRE = re.compile(r'^([A-Za-z]+), ([A-Za-z]+)')
studentChunkRE = re.compile('(Kutztown\nUnofficial Academic Transcript\n.*)(?=Kutztown\nUnofficial Academic Transcript\n)|(Kutztown\nUnofficial Academic Transcript\n.*)$', re.DOTALL)

# put all text of a pdf into a string
with pdfplumber.open(file) as pdf:
    for page in pdf.pages:
        text += page.extract_text()

# split the string across students
allInfo = "bigTranscript.txt"

with open(allInfo,"r") as file:
    string = file.read()
    allStudentList = re.split(studentChunkRE,string)
    allStudentList = filter(None, allStudentList)
    allStudentList = list(filter(len,allStudentList))

pprint(allStudentList[1])

for student in allStudentList:
    # build a list of all a student's courses
    for line in text.split('\n'):
        if honorsRE.match(line) or courseRE.match(line):
            courseList.append(line)

    # join lines where Campus HONORS is on the next line
    for entry in courseList:
        if entry == 'Campus HONORS':
            if newList:
                newList[-1] += ' ' + entry
        else:
            newList.append(entry)

    # build a list of honors courses
    for course in newList:
        if honorsRE.match(course):
            honorsList.append(course)

    cleaned = [s.replace('\n', '') for s in honorsList]

    # parse out a course into pieces of info
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

    # get student names and add it to json
    for line in text.split('\n'):
        if nameRE.match(line):
            line = nameRE.search(line)
            if line:
                lastName = line.group(1)
                firstName = line.group(2)
                studentJSON = {firstName + ' ' + lastName: courseJSON}
    y = json.dumps(studentJSON)

    pprint(studentJSON)

