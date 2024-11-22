import re
import pdfplumber
import csv
import sys

argsNum = len(sys.argv)

inputFile = sys.argv[1] if len(sys.argv) > 1 else "UnofficialTranscript.pdf"
outputFile = sys.argv[2] if len(sys.argv) > 2 else "students_courses.csv"

pdfText = ""

honorsRE = re.compile(r'.*honors', re.IGNORECASE)
courseRE = re.compile(r'[A-Z]+\s\d{2,3}')
courseLineRE = re.compile(r'(\w* \d{4}) ([A-Z]+ \d+) (\w+\s*\w*) ([UGA]*) (\D+?) ([ABCDF-]*)\s?(\d\.\d{3})')
nameRE = re.compile(r'^([A-Za-z]+), ([A-Za-z]+)')
studentChunkRE = re.compile(r'(Kutztown\nUnofficial Academic Transcript\n.*?)(?=Kutztown\nUnofficial Academic Transcript\n)|(Kutztown\nUnofficial Academic Transcript\n.*)$', re.DOTALL)
termGpaRE = re.compile(r'(Current Term) (?:\d*.\d*)* (\d.\d{2})')
cGpaRE = re.compile(r'(Overall) (?:\d*.\d*)* (\d.\d{2})')
termLineRE = re.compile('(Term: )(\w*\s\d{4})')

# put all text of a pdf into a string
with pdfplumber.open(inputFile) as pdf:
    for page in pdf.pages:
        pdfText += page.extract_text() + "\n"

# split the string across students
allStudentList = re.split(studentChunkRE,pdfText)
allStudentList = filter(None, allStudentList)
allStudentList = list(filter(len,allStudentList))

studentNum = 1
wholeJSON = {}

for student in allStudentList:
    studentJSON = {}
    courseList = []
    joinedCourseList = []
    honorsList = []
    studentName = ""
    courseDict = {}
    termList = []
    term = ""
    gpaTermList = []
    cGpa = None
    
    # build a list of all a student's courses
    for line in student.split('\n'):
        if termLineRE.match(line):
            termLine = termLineRE.search(line)
            term = termLine.group(2)
        elif courseRE.match(line):
            line = term + " " + line
            courseList.append(line)
        elif honorsRE.match(line):
            courseList.append(line)
        elif nameRE.match(line):
            line = nameRE.search(line)
            if line:
                lastName = line.group(1)
                firstName = line.group(2)
                studentName = firstName + ' ' + lastName
        elif cGpaRE.match(line):
            cGpaLine = cGpaRE.search(line)
            cGpa = cGpaLine.group(2)
        elif termGpaRE.match(line):
            termGpaLine = termGpaRE.search(line)
            gpaTermList.append(termGpaLine.group(2))
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
    studentJSON["name"] = studentName
    studentJSON["lastTermGPA"] = gpaTermList[-1]
    studentJSON["cumulativeGPA"] = cGpa
    studentJSON["courses"] = courseDict
    wholeJSON[str(studentNum)] = studentJSON
    studentNum += 1
    
# output to csv
with open(outputFile , mode='w', newline='') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
    
    writer.writerow(['Name', 'Current Term GPA', 'Cumulative GPA', 'Course Code', 'Title', 'Grade', 'Credits', 'Term'])
    
    for student_id, student_info in wholeJSON.items():
        name = student_info['name']
        termGPA = student_info['lastTermGPA']
        cGPA = student_info['cumulativeGPA']
        for course_code, course_info in student_info['courses'].items():
            writer.writerow([name, termGPA, cGPA, course_code, course_info['title'], course_info['grade'], course_info['credits'], course_info['term']])