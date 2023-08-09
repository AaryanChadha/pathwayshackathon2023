#Student Matching for Video Chat

import sqlite3
import tkinter as tk
from tkinter import messagebox

conn = sqlite3.connect('student_data.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT,
        study_duration INTEGER,
        timings TEXT,
        subject TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
''')

def insert_student(name, study_duration, timings, subject):
    cursor.execute('''
        INSERT INTO students (name, study_duration, timings, subject)
        VALUES (?, ?, ?, ?)
    ''', (name, study_duration, timings, subject))
    conn.commit()

def find_matching_students(subject):
    cursor.execute('''
        SELECT name, study_duration, timings FROM students WHERE subject = ?
    ''', (subject,))
    matches = cursor.fetchall()
    return matches

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Matcher")
        
        self.login_frame = tk.Frame(root)
        self.login_frame.pack(pady=20)
        
        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10)
        
        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10)
        
        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack(pady=10)
        
        self.register_button = tk.Button(root, text="Register", command=self.register)
        self.register_button.pack(pady=5)
        
        self.logged_in_user = None
        self.student_frame = None
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user_id = cursor.fetchone()
        
        if user_id:
            self.logged_in_user = user_id[0]
            messagebox.showinfo("Login Successful", "Logged in successfully!")
            self.show_student_options()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
    
    def show_student_options(self):
        self.login_frame.destroy()
        
        self.student_frame = tk.Frame(root)
        self.student_frame.pack(pady=20)
        
        self.name_label = tk.Label(self.student_frame, text="Name:")
        self.name_label.grid(row=0, column=0, padx=10)
        self.name_entry = tk.Entry(self.student_frame)
        self.name_entry.grid(row=0, column=1, padx=10)
        
        self.study_label = tk.Label(self.student_frame, text="Study Duration:")
        self.study_label.grid(row=1, column=0, padx=10)
        self.study_entry = tk.Entry(self.student_frame)
        self.study_entry.grid(row=1, column=1, padx=10)
        
        self.timings_label = tk.Label(self.student_frame, text="Timings:")
        self.timings_label.grid(row=2, column=0, padx=10)
        self.timings_entry = tk.Entry(self.student_frame)
        self.timings_entry.grid(row=2, column=1, padx=10)
        
        self.subject_label = tk.Label(self.student_frame, text="Subject:")
        self.subject_label.grid(row=3, column=0, padx=10)
        self.subject_entry = tk.Entry(self.student_frame)
        self.subject_entry.grid(row=3, column=1, padx=10)
        
        self.submit_button = tk.Button(root, text="Submit", command=self.submit_student_data)
        self.submit_button.pack()
        
        self.find_label = tk.Label(root, text="Find Matching Students", font=("Helvetica", 14))
        self.find_label.pack(pady=10)
        
        self.subject_label2 = tk.Label(root, text="Enter Subject:")
        self.subject_label2.pack()
        self.subject_entry2 = tk.Entry(root)
        self.subject_entry2.pack()
        
        self.find_button = tk.Button(root, text="Find Matches", command=self.find_matches)
        self.find_button.pack(pady=10)
        
        self.logout_button = tk.Button(root, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)
    
    def submit_student_data(self):
        name = self.name_entry.get()
        study_duration = int(self.study_entry.get())
        timings = self.timings_entry.get()
        subject = self.subject_entry.get()
        
        insert_student(name, study_duration, timings, subject)
        messagebox.showinfo("Success", "Student data inserted successfully!")
    
    def find_matches(self):
        subject = self.subject_entry2.get()
        matches = find_matching_students(subject)
        
        if matches:
            match_text = "\n".join([f"Name: {match[0]}\nStudy Duration: {match[1]} hours\nTimings: {match[2]}\n" for match in matches])
            messagebox.showinfo("Matching Students", match_text)
        else:
            messagebox.showinfo("No Matches", "No matching students found.")
    
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            messagebox.showerror("Registration Failed", "Username already exists.")
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Registration Successful", "User registered successfully!")
        
    def logout(self):
        if self.student_frame:
            self.student_frame.destroy()
            self.logged_in_user = None
            self.show_login_screen()
    
    def show_login_screen(self):
        self.login_frame = tk.Frame(root)
        self.login_frame.pack(pady=20)
        
        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=10)
        
        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10)
        
        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack(pady=10)
        
        self.register_button = tk.Button(root, text="Register", command=self.register)
        self.register_button.pack(pady=5)
    

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()

conn.close()
