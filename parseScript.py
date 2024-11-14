import re
import pdfplumber
import csv
import sys

argsNum = len(sys.argv)

match argsNum:
    case 1:
        inputFile = "UnofficialTranscript.pdf"
        outputFile  = "students_courses.csv"
    case 2:
        inputFile = sys.argv[1]
    case 3:
        inputFile = sys.argv[1]
        outputFile  = sys.argv[2]
    
pdfText = ""

honorsRE = re.compile(r'.*honors', re.IGNORECASE)
courseRE = re.compile(r'[A-Z]+\s\d{2,3}')
courseLineRE = re.compile(r'(\w* \d{4}) ([A-Z]+ \d+) (\w+\s*\w*) ([UGA]*) (\D+?) ([ABCDF-]*)\s?(\d\.\d{3})')
nameRE = re.compile(r'^([A-Za-z]+), ([A-Za-z]+)')
studentChunkRE = re.compile('(Kutztown\nUnofficial Academic Transcript\n.*?)(?=Kutztown\nUnofficial Academic Transcript\n)|(Kutztown\nUnofficial Academic Transcript\n.*)$', re.DOTALL)

# put all text of a pdf into a string
with pdfplumber.open(inputFile) as pdf:
    for page in pdf.pages:
        pdfText += page.extract_text() + "\n"

# split the string across students
allStudentList = re.split(studentChunkRE,pdfText)
allStudentList = filter(None, allStudentList)
allStudentList = list(filter(len,allStudentList))


termLineRE = re.compile('(Term: )(\w*\s\d{4})')
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
    studentJSON["name"] = studentName
    studentJSON["courses"] = courseDict
    wholeJSON[str(studentNum)] = studentJSON
    studentNum += 1

# output to csv
with open(outputFile , mode='w', newline='') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
    
    writer.writerow(['name', 'course code', 'title', 'grade', 'credits', 'term'])
    
    for student_id, student_info in wholeJSON.items():
        name = student_info['name']
        for course_code, course_info in student_info['courses'].items():
            writer.writerow([name, course_code, course_info['title'], course_info['grade'], course_info['credits'], course_info['term']])