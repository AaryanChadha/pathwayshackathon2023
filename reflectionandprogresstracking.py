import sqlite3
import tkinter as tk
from tkinter import simpledialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

conn = sqlite3.connect("student_journal.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS journal (
    id INTEGER PRIMARY KEY,
    name TEXT,
    date TEXT,
    maths BOOLEAN,
    english BOOLEAN,
    hindi BOOLEAN,
    science BOOLEAN,
    social_studies BOOLEAN,
    maths_marks INTEGER,
    english_marks INTEGER,
    hindi_marks INTEGER,
    science_marks INTEGER,
    social_studies_marks INTEGER,
    reflection TEXT,
    study_intensity TEXT,
    learning TEXT,
    hope TEXT,
    intentions TEXT
)
""")
conn.commit()

root = tk.Tk()
root.title("Student Reflection and Progress Tracking")

def save_data(name, date, subjects, marks, reflection, reflections_extended):
    cursor.execute("""
    INSERT INTO journal (name, date, maths, english, hindi, science, social_studies, maths_marks, english_marks, hindi_marks, science_marks, social_studies_marks, reflection, study_intensity, learning, hope, intentions)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, date, *subjects, *marks, reflection, *reflections_extended))
    conn.commit()

def update_marks():
    update_page = tk.Toplevel(root)
    update_page.title("Update Marks")

    name = simpledialog.askstring("Input", "What is your name?")
    date = simpledialog.askstring("Input", "Enter the date (YYYY-MM-DD) to update:")
    
    new_marks = [
        simpledialog.askinteger("Marks", f"Enter new marks for {subject}:") for subject in ["Maths", "English", "Hindi", "Science", "Social Studies"]
    ]

    cursor.execute("""
    UPDATE journal
    SET maths_marks = ?, english_marks = ?, hindi_marks = ?, science_marks = ?, social_studies_marks = ?
    WHERE name = ? AND date = ?
    """, (*new_marks, name, date))
    conn.commit()
    
    update_page.destroy()

def open_details_page():

def open_analytics():
    analytics_page = tk.Toplevel(root)
    analytics_page.title("Analytics")

    name = simpledialog.askstring("Input", "Enter your name to retrieve analytics:")

    cursor.execute("SELECT * FROM journal WHERE name=?", (name,))
    entries = cursor.fetchall()

    subjects = ["Maths", "English", "Hindi", "Science", "Social Studies"]
    total_marks = [0]*5
    days_studied = [0]*5

    for entry in entries:
        for i, subject in enumerate(subjects):
            if entry[i+2]:  
                days_studied[i] += 1
            total_marks[i] += entry[i+7]  

    avg_marks = [m/days for m, days in zip(total_marks, days_studied) if days != 0] 

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(subjects, avg_marks, marker='o', label='Average Marks')
    ax.plot(subjects, days_studied, marker='x', label='Days Studied', linestyle='--')
    ax.set_title('Average Marks & Days Studied vs Subjects')
    ax.set_ylabel('Counts')
    ax.legend()
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=analytics_page)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()
    canvas.draw()

    analytics_page.mainloop()

start_button = tk.Button(root, text="Start", command=open_details_page)
analytics_button = tk.Button(root, text="Analytics", command=open_analytics)
update_marks_button = tk.Button(root, text="Update Marks", command=update_marks)

start_button.pack(pady=20)
analytics_button.pack(pady=20)
update_marks_button.pack(pady=20)

root.mainloop()
