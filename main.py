import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label
import pdfplumber
import csv
import re
import os
import threading

def open_pdf():
    # Open a file dialog to choose a PDF file
    file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        # Show the processing window
        show_processing_window()

        # Start a thread to process the PDF without freezing the GUI
        threading.Thread(target=process_pdf, args=(file_path,)).start()

def save_csv(wholeJSON):
    # Open a file dialog to choose where to save the CSV file
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_path:
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['name', 'course code', 'title', 'grade', 'credits', 'term'])

            for student_id, student_info in wholeJSON.items():
                name = student_info['name']
                for course_code, course_info in student_info['courses'].items():
                    writer.writerow([name, course_code, course_info['title'], course_info['grade'], course_info['credits'], course_info['term']])

        messagebox.showinfo("Success", f"CSV saved successfully at {save_path}")

def process_pdf(file_path):
    # Extract data from the PDF file using pdfplumber
    # TODO most recent GPA, cumulative GPA
    try:
        text = ""

        honorsRE = re.compile(r'.*honors', re.IGNORECASE)
        courseRE = re.compile(r'[A-Z]+\s\d{2,3}')
        courseLineRE = re.compile(r'(\w* \d{4}) ([A-Z]+ \d+) (\w+\s*\w*) ([UGA]*) (\D+?) ([ABCDFIWNP+-]*)\s?(\d\.\d{3})')
        nameRE = re.compile(r'^([A-Za-z]+), ([A-Za-z]+)')
        studentChunkRE = re.compile('(Kutztown\nUnofficial Academic Transcript\n.*?)(?=Kutztown\nUnofficial Academic Transcript\n)|(Kutztown\nUnofficial Academic Transcript\n.*)$', re.DOTALL)
        termLineRE = re.compile('(Term: )(\w*\s\d{4})')

        # put all text of a pdf into a string
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        # split the string across students
        allStudentList = re.split(studentChunkRE,text)
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

        close_processing_window()
        save_csv(wholeJSON)

    except Exception as e:
        close_processing_window()
        messagebox.showerror("Error", f"An error occurred: {e}")

# Global variable to hold the processing window reference
processing_window = None

def show_processing_window():
    global processing_window
    processing_window = Toplevel()
    processing_window.title("Processing")
    processing_window.geometry("300x100")
    
    # Add a label to the window
    label = Label(processing_window, text="Processing, please wait...")
    label.pack(pady=20)

    # Disable interaction with the main window while processing
    processing_window.grab_set()

def close_processing_window():
    global processing_window
    if processing_window:
        processing_window.destroy()
        processing_window = None

def create_gui():
    # Create the main GUI window
    root = tk.Tk()
    root.title("PDF to CSV Converter")
    root.geometry("300x100")

    # Create a button to trigger the file open dialog
    open_button = tk.Button(root, text="Open PDF", command=open_pdf)
    open_button.pack(pady=20)

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    create_gui()
