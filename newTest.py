import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Label
import pdfplumber
import csv
import os
import threading

def open_pdf():
    file_path = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF files", "*.pdf")])
    if file_path:
        # Show the processing window
        show_processing_window()

        # Start a thread to process the PDF without freezing the GUI
        threading.Thread(target=process_pdf, args=(file_path,)).start()

def save_csv(data):
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if save_path:
        with open(save_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        messagebox.showinfo("Success", f"CSV saved successfully at {save_path}")

def process_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            data = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    data.append(lines)

        flat_data = [line for page in data for line in page]

        # Close the processing window once done
        close_processing_window()

        # Save the CSV file
        save_csv(flat_data)
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
    root = tk.Tk()
    root.title("PDF to CSV Converter")

    open_button = tk.Button(root, text="Open PDF", command=open_pdf)
    open_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
