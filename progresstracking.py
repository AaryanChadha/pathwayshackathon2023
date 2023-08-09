

import sqlite3
import tkinter as tk
from tkinter import simpledialog, messagebox, Text
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
    study_intensity TEXT,
    learning TEXT,
    hope TEXT,
    intentions TEXT,
    general_reflection TEXT
)
""")
conn.commit()

root = tk.Tk()
root.title("Student Reflection and Progress Tracking")

def save_data(name, date, subjects, marks, reflections):
    cursor.execute("""
    INSERT INTO journal (name, date, maths, english, hindi, science, social_studies, maths_marks, english_marks, hindi_marks, science_marks, social_studies_marks, study_intensity, learning, hope, intentions, general_reflection)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, date, *subjects, *marks, *reflections))
    conn.commit()

def update_marks_tab():
    update_page = tk.Toplevel(root)
    update_page.title("Update Marks")

    name = simpledialog.askstring("Input", "What is your name?")
    date = simpledialog.askstring("Input", "Enter the date (YYYY-MM-DD):")

    cursor.execute("SELECT maths, english, hindi, science, social_studies FROM journal WHERE name=? AND date=?", (name, date))
    studied_subjects = cursor.fetchone()

    if not studied_subjects:
        messagebox.showerror("Error", "No data found for this name and date.")
        update_page.destroy()
        return

    subjects = ["Maths", "English", "Hindi", "Science", "Social Studies"]
    selected_subjects = [subjects[i] for i, val in enumerate(studied_subjects) if val]

    new_marks = {}
    for subject in selected_subjects:
        mark = simpledialog.askinteger("Marks", f"Update marks for {subject}:")
        new_marks[subject.lower() + "_marks"] = mark

    update_stmt = "UPDATE journal SET " + ", ".join([f"{key} = ?" for key in new_marks.keys()]) + " WHERE name = ? AND date = ?"
    cursor.execute(update_stmt, (*new_marks.values(), name, date))
    conn.commit()

    messagebox.showinfo("Updated", "Marks updated successfully.")
    update_page.destroy()

    pass

def view_reflections():
    view_page = tk.Toplevel(root)
    view_page.title("View Reflections")
    
    name = simpledialog.askstring("Input", "Enter your name:")
    date = simpledialog.askstring("Input", "Enter the date (YYYY-MM-DD):")
    
    cursor.execute("SELECT study_intensity, learning, hope, intentions, general_reflection FROM journal WHERE name=? AND date=?", (name, date))
    entries = cursor.fetchone()
    
    if entries:
        for idx, label in enumerate(["Study Intensity", "Learning", "Hope", "Intentions", "General Reflection"]):
            tk.Label(view_page, text=f"{label}: {entries[idx]}").pack(pady=10)
    else:
        messagebox.showerror("Error", "No data found for this date.")
    
    view_page.mainloop()

def analytics_tab():
    analytics_page = tk.Toplevel(root)
    analytics_page.title("Analytics")

    name = simpledialog.askstring("Input", "Enter your name to retrieve analytics:")

    cursor.execute("SELECT * FROM journal WHERE name=?", (name,))
    entries = cursor.fetchall()

    if not entries:
        messagebox.showerror("Error", "No data found for this name.")
        return

    subjects = ["Maths", "English", "Hindi", "Science", "Social Studies"]
    total_marks = [0]*5
    days_studied = [0]*5

    for entry in entries:
        for i, subject in enumerate(subjects):
            if entry[i+2]:
                days_studied[i] += 1
            total_marks[i] += entry[i+7]

    avg_marks = [m/d for m, d in zip(total_marks, days_studied) if d != 0]

    fig, ax = plt.subplots(figsize=(6, 4))
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

def start_tab():
    details_page = tk.Toplevel(root)
    details_page.title("Details")

    name = simpledialog.askstring("Input", "What is your name?")
    date = simpledialog.askstring("Input", "Enter the date (YYYY-MM-DD):")

    subjects_vars = [tk.BooleanVar() for _ in ["Maths", "English", "Hindi", "Science", "Social Studies"]]

    for idx, subject in enumerate(["Maths", "English", "Hindi", "Science", "Social Studies"]):
        tk.Checkbutton(details_page, text=subject, variable=subjects_vars[idx]).pack()

    marks = [
        simpledialog.askinteger("Marks", f"Enter marks for {subject}:") for subject in ["Maths", "English", "Hindi", "Science", "Social Studies"]
    ]

    reflection_prompts = [
        simpledialog.askstring("Reflection", prompt) for prompt in [
            "How hard did you study today?",
            "What did you learn today?",
            "What are you hopeful for?",
            "What are your intentions for tomorrow?",
        ]
    ]
    
    general_reflection = simpledialog.askstring("Reflection", "Enter your general reflection:")
    
    save_data(name, date, [s.get() for s in subjects_vars], marks, reflection_prompts + [general_reflection])

start_button = tk.Button(root, text="Start", command=start_tab)
analytics_button = tk.Button(root, text="Analytics", command=analytics_tab)
update_marks_button = tk.Button(root, text="Update Marks", command=update_marks_tab)
view_reflection_button = tk.Button(root, text="View Reflections", command=view_reflections)

start_button.pack(pady=20)
analytics_button.pack(pady=20)
update_marks_button.pack(pady=20)
view_reflection_button.pack(pady=20)

root.mainloop()
