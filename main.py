import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label
import pdfplumber
import csv
import re
import os
import threading

# TODO Add major. Add "Overall credits" and total honors credits. Don't count B- or worse. 
def openPdf():
    filePaths = filedialog.askopenfilenames(title="Select one or more PDF files", filetypes=[("PDF files", "*.pdf")])
    if filePaths:
        showProcessingWindow()

        # Start a thread to process the PDF without freezing the GUI
        threading.Thread(target=processPdf, args=(filePaths,)).start()

def saveCsv(wholeJSON):
    savePath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if savePath:
        with open(savePath, mode='w', newline='') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Name', 'Current Term GPA', 'Cumulative GPA', 'Course Code', 'Title', 'Grade', 'Credits', 'Term', 'Total Credits'])

            acceptableGrades = ["A+", "A", "A-", "B+", "B"]

            for student_id, student_info in wholeJSON.items():
                name = student_info['name']
                termGPA = student_info['lastTermGPA']
                cGPA = student_info['cumulativeGPA']
                totalCredits = student_info['totalCredits']
                for course_code, course_info in student_info['courses'].items():
                    writer.writerow([name, termGPA, cGPA, course_code, course_info['title'], course_info['grade'], course_info['credits'], course_info['term'], totalCredits])
            
        messagebox.showinfo("Success", f"CSV saved successfully at {savePath}")

def extractText(file_paths):
    # put all text of a pdf into a string
    pdfText = ""
    for file_path in file_paths:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                pdfText += page.extract_text() + "\n"
    return pdfText

def processPdf(filePaths):
    try:
        combinedPdfText = extractText(filePaths)

        studentChunkRE = re.compile(r'(Kutztown\nUnofficial Academic Transcript\n.*?)(?=Kutztown\nUnofficial Academic Transcript\n)|(Kutztown\nUnofficial Academic Transcript\n.*)$', re.DOTALL)
        honorsRE = re.compile(r'.*honors', re.IGNORECASE)
        courseRE = re.compile(r'[A-Z]+\s\d{2,3}')
        courseLineRE = re.compile(r'(\w* \d{4}) ([A-Z]+ \d+) (\w+\s*\w*) ([UGA]*) (\D+?) ([ABCDFIWNP+-]*)\s?(\d\.\d{3})')
        nameRE = re.compile(r'^([A-Za-z]+), ([A-Za-z]+)')
        termGpaRE = re.compile(r'(Current Term) (?:\d*.\d*)* (\d.\d{2})')
        # cGpaRE = re.compile(r'(Overall) (?:\d*.\d*)* (\d.\d{2})')
        termLineRE = re.compile(r'(Term: )(\w*\s\d{4})')
        # totalCreditsRE = re.compile(r'Overall (\d*.\d*) (\d*.\d*) (\d*.\d*) (\d*.\d*) (\d*.\d*) (\d*.\d*)')
        overallRE = re.compile(r'(Overall )(?:\d*?.\d*? ){2}(\d*.\d*) (?:\d*?.\d*? ){2}(\d.\d{2})')
        # split the string across students
        allStudentList = re.split(studentChunkRE, combinedPdfText)
        allStudentList = filter(None, allStudentList)
        allStudentList = list(filter(len, allStudentList))

        studentNum = 1
        wholeJSON = {}

        for student in allStudentList:
            studentJSON = {}
            courseList = []
            joinedCourseList = []
            honorsList = []
            studentName = ""
            courseDict = {}
            term = ""
            gpaTermList = []
            cGpa = None
            totalCredits = 0
            
            # use REs to grab needed data
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
                elif overallRE.match(line):
                    overallLine = overallRE.search(line)
                    totalCredits = overallLine.group(2)
                    cGpa = overallLine.group(3)
                elif termGpaRE.match(line):
                    termGpaLine = termGpaRE.search(line)
                    gpaTermList.append(termGpaLine.group(2))
                # exclude everything else like intermediate GPA, quality points, etc
                
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

            # add info to JSON
            studentJSON["name"] = studentName
            studentJSON["lastTermGPA"] = gpaTermList[-1]
            studentJSON["cumulativeGPA"] = cGpa
            studentJSON["totalCredits"] = totalCredits
            studentJSON["courses"] = courseDict
            wholeJSON[str(studentNum)] = studentJSON
            studentNum += 1

        closeProcessingWindow()
        saveCsv(wholeJSON)

    except Exception as e:
        closeProcessingWindow()
        messagebox.showerror("Error", f"An error occurred: {e}")

processing_window = None

def showProcessingWindow():
    global processing_window
    processing_window = Toplevel()
    processing_window.title("Processing")
    processing_window.geometry("300x100")
    
    label = Label(processing_window, text="Processing, please wait...")
    label.pack(pady=20)

    # Disable interaction with the main window while processing
    processing_window.grab_set()

def closeProcessingWindow():
    global processing_window
    if processing_window:
        processing_window.destroy()
        processing_window = None

def createGui():
    # Create the main GUI window
    root = tk.Tk()
    root.title("Transcriptr")
    root.geometry("300x100")

    open_button = tk.Button(root, text="Open PDF(s)", command=openPdf)
    open_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    createGui()
