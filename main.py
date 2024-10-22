import re
import pdfplumber
import json
from pprint import pprint

file = "bigUnofficialTranscript.pdf"
text = ""

honorsRE = re.compile(r'.*honors', re.IGNORECASE)
courseRE = re.compile(r'[A-Z]+\s\d{2,3}')
courseLineRE = re.compile(r'(\w* \d{4}) ([A-Z]+ \d+) (\w+\s*\w*) ([UGA]*) (\D+?) ([ABCDF-]*)\s?(\d\.\d{3})')
nameRE = re.compile(r'^([A-Za-z]+), ([A-Za-z]+)')
studentChunkRE = re.compile('(Kutztown\nUnofficial Academic Transcript\n.*?)(?=Kutztown\nUnofficial Academic Transcript\n)|(Kutztown\nUnofficial Academic Transcript\n.*)$', re.DOTALL)

# put all text of a pdf into a string
with pdfplumber.open(file) as pdf:
    for page in pdf.pages:
        text += page.extract_text() + "\n"

# split the string across students
allStudentList = re.split(studentChunkRE,text)
allStudentList = filter(None, allStudentList)
allStudentList = list(filter(len,allStudentList))

studentJSON = {}
termLineRE = re.compile('(Term: )(\w*\s\d{4})')

for student in allStudentList:
    courseList = []
    joinedCourseList = []
    honorsList = []
    studentName = ""
    courseDict = {}
    termList = []
    term = ""

    # build a list of all a student's courses
    for line in student.split('\n'):
        if termLineRE.match(line):
            termLine = termLineRE.search(line)
            term = termLine.group(2)
        if courseRE.match(line):
            line = term + " " + line
            courseList.append(line)
        if honorsRE.match(line):
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
                term = course.group(1)
                courseCode = course.group(2)
                title = course.group(5)
                grade = course.group(6)
                creditHours = course.group(7)
                courseDict[courseCode] = {"term": term, "title": title, "grade": grade, "credits": creditHours}
    # print(courseDict)
    studentJSON[studentName] = courseDict

# pprint(studentJSON)

# actualJSON = json.dumps(studentJSON, indent=2)
# print(actualJSON)



