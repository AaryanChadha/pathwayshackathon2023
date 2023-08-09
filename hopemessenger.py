import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import geopy
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
import random
import string
import folium
import webbrowser

geolocator = Nominatim(user_agent="geoapiExercises")

def geolocation(city):
    try:
        return geolocator.geocode(city)
    except GeocoderTimedOut:
        return geolocation(city)

def random_username(length=5):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

connection = sqlite3.connect('hopemessenger.db')
c = connection.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, location TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS messages (username TEXT, message TEXT, location TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS DMs (sender TEXT, receiver TEXT, message TEXT)")

root = tk.Tk()
root.geometry("400x600")
root.title("New Hope Messenger")

style = ttk.Style()
style.configure('TButton', background='lightblue', foreground='black')
style.configure('TLabel', background='lightblue', foreground='black')
root.configure(bg='lightblue')

notifications = []
current_username = None

def click_sign_up():
    username = username_entry.get()
    location = location_entry.get()

    if not username or not location:
        messagebox.showerror(title="Error", message="You must fill out all fields!")
        return

    try:
        c.execute("INSERT INTO users (username, location) VALUES (?, ?)", (username, location))
    except sqlite3.IntegrityError:
        messagebox.showerror(title="Error", message=f"Username {username} is already taken!")
        return

    connection.commit()
    show_main_app()

def click_login():
    global current_username, username_entry
    username = username_entry.get()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    account = c.fetchone()

    if account:
        current_username = username
        show_main_app()
    else:
        messagebox.showerror(title="Error", message="Account not found!")

def click_send_message():
    global message_entry, location_entry
    message = message_entry.get()
    location_name = location_entry.get()
    location = geolocation(location_name)
    if not location:
        messagebox.showerror(title="Error", message="Could not find location")
        return
    c.execute("INSERT INTO messages (username, message, location) VALUES (?, ?, ?)", (current_username, message, location_name))
    connection.commit()
    message_entry.delete(0, 'end')
    location_entry.delete(0, 'end')

def show_login_page():
    global username_entry, location_entry
    for widget in root.winfo_children():
        widget.destroy()

    ttk.Label(root, text="Welcome to New Hope Messenger", font=("Arial", 16)).pack(pady=15)

    ttk.Label(root, text="Username:").pack(pady=5)
    username_entry = ttk.Entry(root, width=40)
    username_entry.pack(pady=5)

    ttk.Label(root, text="Location (for sign-up only):").pack(pady=5)
    location_entry = ttk.Entry(root, width=40)
    location_entry.pack(pady=5)

    ttk.Button(root, text="Sign Up", command=click_sign_up).pack(pady=5)
    ttk.Button(root, text="Login", command=click_login).pack(pady=5)

def show_main_app():
    global message_entry, location_entry

    for widget in root.winfo_children():
        widget.destroy()

    ttk.Label(root, text=f"Welcome {current_username}!", font=("Arial", 16)).pack(pady=15)

    ttk.Label(root, text="Message:").pack(pady=5)
    message_entry = ttk.Entry(root, width=40)
    message_entry.pack(pady=5)

    ttk.Label(root, text="Location:").pack(pady=5)
    location_entry = ttk.Entry(root, width=40)
    location_entry.pack(pady=5)

    ttk.Button(root, text="Send Message", command=click_send_message).pack(pady=5)
    ttk.Button(root, text="View Messages on Map", command=show_map).pack(pady=5)
    ttk.Button(root, text="Message Board", command=show_message_board).pack(pady=5)
    ttk.Button(root, text="DMs", command=show_DMs_page).pack(pady=5)
    ttk.Button(root, text="Sign Out", command=show_login_page).pack(pady=5)

    root.after(30000, notify_new_message)

def notify_new_message():
    c.execute("SELECT * FROM messages")
    all_messages = c.fetchall()

    for msg in all_messages:
        if msg not in notifications:
            notifications.append(msg)
            print(f"New message from {msg[0]} at {msg[2]}: {msg[1]}")

def show_map():
    map_obj = folium.Map(location=[0, 0], zoom_start=2)
    c.execute("SELECT * FROM messages")
    rows = c.fetchall()
    for row in rows:
        location = geolocation(row[2])
        if location:
            folium.Marker(
                location=[location.latitude, location.longitude],
                popup=f"User: {row[0]} \n Message: {row[1]}",
                icon=folium.Icon(icon="cloud"),
            ).add_to(map_obj)
    map_obj.save('map.html')
    webbrowser.open('map.html')

def show_message_board():
    board_window = tk.Toplevel(root)
    board_window.title("Message Board")
    board_window.geometry("700x600")

    ttk.Label(board_window, text="Username", width=20).grid(row=0, column=0, padx=5, pady=5)
    ttk.Label(board_window, text="Message", width=40).grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(board_window, text="Location", width=20).grid(row=0, column=2, padx=5, pady=5)

    c.execute("SELECT * FROM messages")
    messages = c.fetchall()

    for idx, msg in enumerate(messages):
        ttk.Label(board_window, text=msg[0], width=20).grid(row=idx+1, column=0, padx=5, pady=5)
        ttk.Label(board_window, text=msg[1], width=40).grid(row=idx+1, column=1, padx=5, pady=5)
        ttk.Label(board_window, text=msg[2], width=20).grid(row=idx+1, column=2, padx=5, pady=5)

def show_DMs_page():
    dm_window = tk.Toplevel(root)
    dm_window.title(f"Direct Messages for {current_username}")

    ttk.Label(dm_window, text="Direct Message someone:").pack(pady=5)
    dm_username_entry = ttk.Entry(dm_window, width=20)
    dm_username_entry.pack(pady=5)

    listbox = tk.Listbox(dm_window)
    listbox.pack(pady=20)

    c.execute("SELECT DISTINCT sender, receiver FROM DMs WHERE sender=? OR receiver=?", (current_username, current_username))
    known_chats = c.fetchall()

    for chat in known_chats:
        partner = chat[1] if chat[0] == current_username else chat[0]
        listbox.insert(tk.END, partner)

    def send_dm():
        dm_username = dm_username_entry.get().strip()
        if dm_username == current_username:
            messagebox.showerror(title="Error", message="Cannot send message to oneself!")
            return
        c.execute("SELECT * FROM users WHERE username=?", (dm_username,))
        user = c.fetchone()
        if user:
            if dm_username not in listbox.get(0, tk.END):
                listbox.insert(tk.END, dm_username)
            display_dm_interface(dm_username)
        else:
            messagebox.showerror(title="Error", message="Username does not exist. Please enter a valid username.")
            return

    ttk.Button(dm_window, text="Start DM", command=send_dm).pack(pady=5)

    def open_chat(evt):
        partner = listbox.get(listbox.curselection())
        display_dm_interface(partner)

    listbox.bind('<Double-Button-1>', open_chat)

def notify_new_message():
    if notifications:
        if messagebox.askyesno("Notification", "You have new messages. Do you want to check them?"):
            show_DMs_page()

def display_dm_interface(partner_username):
    dm_chat_window = tk.Toplevel(root)
    dm_chat_window.title(f"Chat with {partner_username}")

    messages_textbox = tk.Text(dm_chat_window, height=20, width=50)
    messages_textbox.pack(pady=10)

    input_frame = tk.Frame(dm_chat_window)
    input_frame.pack(pady=5)

    dm_entry = ttk.Entry(input_frame, width=40)
    dm_entry.pack(side=tk.LEFT, padx=5)

    def load_chat_history():
        messages_textbox.config(state=tk.NORMAL)
        messages_textbox.delete(1.0, tk.END)

        c.execute("SELECT sender, message FROM DMs WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)", (current_username, partner_username, partner_username, current_username))
        messages = c.fetchall()
        for msg in messages:
            messages_textbox.insert(tk.END, f"{msg[0]}: {msg[1]}\n")

        messages_textbox.config(state=tk.DISABLED)

    def send_dm_message():
        message = dm_entry.get().strip()
        if not message:
            return
        c.execute("INSERT INTO DMs (sender, receiver, message) VALUES (?, ?, ?)", (current_username, partner_username, message))
        connection.commit()
        dm_entry.delete(0, tk.END)
        load_chat_history()

    send_button = ttk.Button(input_frame, text="Send", command=send_dm_message)
    send_button.pack(side=tk.LEFT)

    load_chat_history()

    def refresh_chat():
        load_chat_history()
        dm_chat_window.after(5000, refresh_chat)

    refresh_chat()

show_login_page()
root.mainloop()
