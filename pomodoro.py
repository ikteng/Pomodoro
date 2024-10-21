import tkinter as tk
from time import strftime
import sqlite3
from tkinter import filedialog
import pygame
from PIL import Image,ImageTk

# Database connection and table creation
conn = sqlite3.connect(r'tasks.db') # change this to the location of this file such as 'pomodoro\tasks.db'
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT)''')
conn.commit()

# Existing tasks retrieval function
def load_tasks():
    c.execute('''SELECT task FROM tasks''')
    tasks = c.fetchall()
    return [task[0] for task in tasks]

# Save new task to the database
def save_task(task):
    c.execute('''INSERT INTO tasks (task) VALUES (?)''', (task,))
    conn.commit()

root = tk.Tk()
root.title('Pomodoro')

# declare variables
current_task = tk.StringVar()
current_task.set('')

timer_running = False
timer_id = None 

work_timer_var = tk.StringVar()
work_timer_var.set("25:00")

rest_timer_var = tk.StringVar()
rest_timer_var.set("05:00")

# function for current time 
def update_clock(label):
    label.config(text=strftime('%H:%M:%S %p'))
    label.after(1000, lambda: update_clock(label))

# function for current date
def update_date(label):
    label.config(text=strftime('%A, %B %d, %Y'))  # Format the date as desired
    label.after(1000, lambda: update_date(label))

# function for updating timer
def update_timer(timer_var, decrement):
    alarm_path = r"Pomodoro\media\alarm_sound.mp3"
    current_time = timer_var.get()
    mins, secs = map(int, current_time.split(":"))
    total_secs = mins * 60 + secs
    total_secs -= decrement  # decrease the total secs

    if total_secs <= 0:
        timer_var.set("00:00")
        # play alarm sound
        if alarm_path:
            pygame.mixer.init()
            pygame.mixer.music.load(alarm_path)
            pygame.mixer.music.set_volume(0.5)  # Set the volume (0.0 to 1.0)
            pygame.mixer.music.play()

            # Schedule a function to stop the sound after 5 seconds
            root.after(5000, lambda: stop_alarm())
        return

    mins = total_secs // 60
    secs = total_secs % 60
    new_time = f"{mins:02d}:{secs:02d}"
    timer_var.set(new_time)

# function to work the timer
def toggle_timer(timer_var, btn):
    global timer_running
    global timer_id

    if not timer_running:
        if timer_var.get() != "00:00":  # Check if timer is not already at 00:00
            def update():
                update_timer(timer_var, 1)
                if timer_var.get() != "00:00":
                    global timer_id
                    timer_id = root.after(1000, update)

            update()
            timer_running = True
            btn.config(text="Stop Timer")
    else:
        root.after_cancel(timer_id)
        timer_running = False
        stop_alarm() # stop the alarm sound
        if timer_var.get() != "00:00":
            btn.config(text="Start Timer")
        else:
            timer_var.set("25:00" if timer_var == work_timer_var else "05:00")
            btn.config(text="Start Timer")

# stop alarm sound
def stop_alarm():
    pygame.mixer.music.stop()

# function for the to-do list
def setup_todo_list():
    middle_frame = tk.Frame(root)
    middle_frame.grid(row=0, column=1, rowspan=8)

    frame = tk.Frame(middle_frame)
    frame.grid(row=0, column=0, sticky='nsew')

    listbox = tk.Listbox(frame, width=40, height=17, bd=0, font=("Helvetica", 12))
    listbox.grid(row=0, column=0, columnspan=8, sticky='nsew')

    scrollbar = tk.Scrollbar(frame)
    scrollbar.grid(row=0, column=5, sticky='ns')
    listbox.config(yscrollcommand=scrollbar.set)

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)

    scrollbar.config(command=listbox.yview)

    # Load existing tasks from the database and populate the listbox
    existing_tasks = load_tasks()
    for task in existing_tasks:
        listbox.insert(tk.END, task)

    # function to add task to the to-do list
    def add_task():
        task = entry.get()
        if task:
            listbox.insert(tk.END, task)
            entry.delete(0, tk.END)

    # function to delete task from to-do list
    def delete_task():
        try:
            task_index = listbox.curselection()[0]
            listbox.delete(task_index)
        except IndexError:
            pass

    # function to edit task from the to-do list
    def edit_task():
        try:
            task_index = listbox.curselection()[0]
            selected_task = listbox.get(task_index)
            entry.delete(0, tk.END)
            entry.insert(tk.END, selected_task)
            listbox.delete(task_index)
        except IndexError:
            pass
    
    # function to strike off tasks instead of deleting them
    def strike_off():
        def strike(text):
            return ''.join([u'\u0336{}'.format(c) for c in text])

        try:
            task_index = listbox.curselection()[0]
            selected_task = listbox.get(task_index)

            if u'\u0336' in selected_task:
                # Task is already struck through, remove the strike-through effect
                task_without_strike = selected_task.replace(u'\u0336', '')
                listbox.delete(task_index)
                listbox.insert(task_index, task_without_strike)
            else:
                # Task is not struck through, apply the strike-through effect
                strikethrough_text = strike(selected_task)
                listbox.delete(task_index)
                listbox.insert(task_index, strikethrough_text)
        except IndexError:
            pass

    # function to move task up
    def move_up():
        try:
            task_index = listbox.curselection()[0]
            if task_index > 0:
                task = listbox.get(task_index)
                listbox.delete(task_index)
                listbox.insert(task_index - 1, task)
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(task_index - 1)
        except IndexError:
            pass
    
    # function to move task down
    def move_down():
        try:
            task_index = listbox.curselection()[0]
            if task_index < listbox.size() - 1:
                task = listbox.get(task_index)
                listbox.delete(task_index)
                listbox.insert(task_index + 1, task)
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(task_index + 1)
        except IndexError:
            pass

    # entry to enter task
    entry = tk.Entry(middle_frame, width=30, font=("Helvetica", 12))
    entry.grid(row=1, column=0, padx=10, pady=10, columnspan=3, sticky='ew')

    # Create a frame for buttons under the entry
    button_frame = tk.Frame(middle_frame)
    button_frame.grid(row=2, column=0, columnspan=3, pady=5)

    add_button = tk.Button(button_frame, text="➕", width=5, command=add_task)
    add_button.grid(row=0, column=0, padx=5)

    delete_button = tk.Button(button_frame, text="🗑️", width=5,command=delete_task)
    delete_button.grid(row=0, column=1, padx=5)

    edit_button = tk.Button(button_frame, text="✏️", width=5,command=edit_task)
    edit_button.grid(row=0, column=2, padx=5)

    strike_button = tk.Button(button_frame, text="₭", width=5,command=strike_off)
    strike_button.grid(row=0, column=3, padx=5)

    up_button = tk.Button(button_frame, text="⬆️", width=5,command=move_up)
    up_button.grid(row=0, column=4, padx=5)

    down_button = tk.Button(button_frame, text="⬇️", width=5,command=move_down)
    down_button.grid(row=0, column=5, padx=5)
    
    return listbox

# Function to extract filename from path
def extract_filename(path):
    return path.split("/")[-1]  # Split the path and extract the filename

# Function to select audio file
def select_audio_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3;*.wav")])
    if file_path:
        global current_audio_file
        current_audio_file = file_path
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_volume(0.5)  # Set the volume (0.0 to 1.0)
        pygame.mixer.music.play(-1)  # Play in an infinite loop (-1)
        
        # Initialize rotation_angle before calling rotate_image()
        rotation_angle = 0

        # Start the rotation animation
        rotate_image(rotation_angle)
        audio_file_label.config(text=f"Currently playing: {extract_filename(file_path)}")

# function to play audio after pausing it
def play_audio():
    pygame.mixer.music.unpause()  # Resume playback
    rotate_image(rotation_angle)  # Resume rotation from the last angle
    audio_file_label.config(text=f"Currently playing: {extract_filename(current_audio_file)}")

# function to pause the audio which can be replayed
def pause_audio():
    pygame.mixer.music.pause()  # Pause playback

    # Stop the rotation when audio is paused
    root.after_cancel(rotation_id)
    audio_file_label.config(text=f"Paused: {extract_filename(current_audio_file)}")

# function to stop audio
def stop_audio():
    pygame.mixer.music.stop()  # Stop playback
    pygame.mixer.quit()  # Quit Pygame mixer

    # Stop the rotation when audio is stopped
    root.after_cancel(rotation_id)
    audio_file_label.config(text="Stopped")

# function to rotate image when audio is playing
def rotate_image(angle=None):
    global rotated_image, image_on_canvas, rotation_speed, rotation_angle, rotation_id
    if angle is not None:
        rotation_angle = angle

    rotated_image = original_image.rotate(rotation_angle)
    image_on_canvas = ImageTk.PhotoImage(rotated_image)
    canvas.itemconfig(image_item, image=image_on_canvas)
    rotation_angle += rotation_speed
    if rotation_angle >= 360:
        rotation_angle = 0
    rotation_id = root.after(50, rotate_image, rotation_angle)  # Pass rotation_angle as an argument  # Re-schedule the rotation

# function to save remaining tasks to the database
def save_tasks_to_db():
    tasks = middle_frame.get(0, tk.END)  # Get all tasks from the listbox
    c.execute('''DELETE FROM tasks''')  # Clear existing tasks in the database
    for task in tasks:
        save_task(task.strip())  # Save each task to the database
    conn.commit()

# save remaining tasks on the to-do list when closing
def on_closing():
    save_tasks_to_db()
    root.destroy()

work_timer_frame = tk.Frame(root)
work_timer_frame.grid(row=0, column=0, padx=10, pady=10)

work_timer_lbl = tk.Label(work_timer_frame, font=("calibri", 20, ""), text="Work Timer:")
work_timer_lbl.grid(row=0, column=0, padx=10)

work_timer_entry = tk.Entry(work_timer_frame, font=("calibri", 15, ""), textvariable=work_timer_var, state='readonly')
work_timer_entry.grid(row=1, column=0, padx=10)

work_start_btn = tk.Button(work_timer_frame, text="Start Timer", command=lambda: toggle_timer(work_timer_var, work_start_btn))
work_start_btn.grid(row=2, column=0, padx=10)

rest_timer_frame = tk.Frame(root)
rest_timer_frame.grid(row=1, column=0, padx=10, pady=10)

rest_timer_lbl = tk.Label(rest_timer_frame, font=("calibri", 20, ""), text="Rest Timer:")
rest_timer_lbl.grid(row=0, column=0, padx=10)

rest_timer_entry = tk.Entry(rest_timer_frame, font=("calibri", 15, ""), textvariable=rest_timer_var, state='readonly')
rest_timer_entry.grid(row=1, column=0, padx=10)

rest_start_btn = tk.Button(rest_timer_frame, text="Start Timer", command=lambda: toggle_timer(rest_timer_var, rest_start_btn))
rest_start_btn.grid(row=2, column=0, padx=10)

middle_frame = setup_todo_list()
middle_frame.grid(row=0, column=1)

current_frame = tk.Frame(root)
current_frame.grid(row=0, column=2, padx=10)

current_date_lbl = tk.Label(current_frame, font=('calibri', 10))
current_date_lbl.grid(row=1, column=0) 
update_date(current_date_lbl)  # Start updating the date label

current_time_lbl = tk.Label(current_frame, font=('calibri', 20))
current_time_lbl.grid(row=2, column=0)
update_clock(current_time_lbl) # start updating the current time label

# Create a frame for audio selection below the current time
audio_frame = tk.Frame(root)
audio_frame.grid(row=1, column=2, padx=10, pady=10)

audio_button = tk.Button(audio_frame, text="Browse", command=select_audio_file)
audio_button.grid(row=0, column=0,columnspan=3,padx=5)

audio_file_label = tk.Label(audio_frame, text="", font=("calibri", 8))
audio_file_label.grid(row=1, column=0, columnspan=3, padx=5)

# Load the image
original_image = Image.open('Pomodoro\media\disc.png')
rotated_image = original_image

# Create a Canvas to display the rotating image
canvas = tk.Canvas(audio_frame, width=200, height=200)
canvas.grid(row=2,column=0, columnspan=3, padx=5,pady=5)

# Create an initial ImageTk PhotoImage and display it on the canvas
image_on_canvas = ImageTk.PhotoImage(rotated_image)
image_item = canvas.create_image(100, 100, image=image_on_canvas)

# Set rotation speed (adjust this value as needed)
rotation_speed = 1

# Create buttons for play, pause, and stop audio
play_button = tk.Button(audio_frame, text="▶️", width=5, command=play_audio)
play_button.grid(row=3, column=0, padx=5, pady=5)

pause_button = tk.Button(audio_frame, text="⏸️", width=5, command=pause_audio)
pause_button.grid(row=3, column=1, padx=5, pady=5)

stop_button = tk.Button(audio_frame, text="⏹️", width=5, command=stop_audio)
stop_button.grid(row=3, column=2, padx=5, pady=5)

# Use grid_rowconfigure and grid_columnconfigure to configure row and column weights
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.protocol("WM_DELETE_WINDOW", on_closing)  # Call on_closing function when the window is closed

root.mainloop()
