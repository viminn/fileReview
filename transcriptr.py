import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label
import pdfplumber
import csv
import re
import os
import threading

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
            writer.writerow(['Name', 'Latest Major', 'Course Code', 'Title', 'Grade Earned', 'Credits Earned', 'Term', 'Latest Term GPA', 'Cumulative GPA', 'Total Honors Credits', 'Total Credits'])

            for student_id, student_info in wholeJSON.items():
                name = student_info['name']
                termGPA = student_info['lastTermGPA']
                cGPA = student_info['cumulativeGPA']
                totalCredits = student_info['totalCredits']
                honorsCredits = student_info['honorsCredits']
                major = student_info['major']
                for course_code, course_info in student_info['courses'].items():
                    writer.writerow([name, major, course_code, course_info['title'], course_info['grade'], course_info['credits'], course_info['term'], termGPA, cGPA, honorsCredits, totalCredits])
            
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
        nameRE = re.compile(r'(Name Birth Date\n)(.*), (.*) ')
        majorRE = re.compile(r'Major\n(.*$)', re.MULTILINE)
        termGpaRE = re.compile(r'(Current Term) (?:\d*.\d*)* (\d.\d{2})')
        termLineRE = re.compile(r'(Term: )(\w*\s\d{4})')
        overallRE = re.compile(r'(Overall )(?:\d*?.\d*? ){2}(\d*.\d*) (?:\d*?.\d*? ){2}(\d.\d{2})')

        # split the string across students
        allStudentList = re.split(studentChunkRE, combinedPdfText)
        allStudentList = filter(None, allStudentList)
        allStudentList = list(filter(len, allStudentList))

        studentNum = 1
        wholeJSON = {}
        acceptableGrades = ["A+", "A", "A-", "B+", "B", "P"]

        for student in allStudentList:
            studentJSON = {}
            courseList = []
            honorsList = []
            studentName = ""
            courseDict = {}
            term = ""
            gpaTermList = []
            cGpa = 0
            totalCredits = 0
            honorsCredits = 0
            
            # Find all matches at once for each pattern
            term_matches = termLineRE.findall(student)
            name_matches = nameRE.findall(student)  
            major_matches = majorRE.findall(student)
            overall_matches = overallRE.findall(student)
            termGpa_matches = termGpaRE.findall(student)
            
            # Process matches
            if term_matches:
                term = term_matches[-1][1] 
            
            if name_matches:
                lastName, firstName = name_matches[-1][1:] 
                studentName = f"{firstName} {lastName}"

            majorsList = [major for major in major_matches]  
            latestMajor = majorsList[-1]

            if overall_matches:
                totalCredits, cGpa = overall_matches[-1][1], overall_matches[-1][2]

            gpaTermList = [gpa[1] for gpa in termGpa_matches] 
            lastTermGPA = gpaTermList[-1]

            # Grab data that must be looked at line by line
            for line in student.split('\n'):
                if termLineRE.match(line):
                    termLine = termLineRE.search(line)
                    term = termLine.group(2)
                if courseRE.match(line):
                    line = term + " " + line
                    courseList.append(line)
                if honorsRE.match(line):
                    if line != courseList[-1]:
                        courseList[-1] += ' ' + line
                        honorsList.append(courseList[-1])
                    else:
                        honorsList.append(courseList[-1])
            # Exclude everything else like intermediate GPA, quality points, etc

            cleanedHonorsList = [s.replace('\n', '') for s in honorsList]
            
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
                        if grade in acceptableGrades:
                            honorsCredits += int(float(creditHours))

            # add info to JSON
            studentJSON["name"] = studentName
            studentJSON["major"] = latestMajor
            studentJSON["lastTermGPA"] = lastTermGPA
            studentJSON["cumulativeGPA"] = cGpa
            studentJSON["totalCredits"] = totalCredits
            studentJSON["honorsCredits"] = honorsCredits
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
