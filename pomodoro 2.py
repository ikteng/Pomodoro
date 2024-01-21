import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QTabWidget, QListWidget, QHBoxLayout, QLineEdit, QInputDialog, QScrollArea
from PyQt5.QtCore import QTimer, QTime, Qt
import sqlite3

class TimerWidget(QWidget):
    def __init__(self, label_text, initial_duration, switch_tab_function, parent=None):
        super().__init__(parent)
        self.duration = initial_duration
        self.switch_tab_function = switch_tab_function

        # Label for the type of timer (e.g., "Work Timer" or "Rest Timer")
        self.label_type = QLabel(label_text, self)
        self.label_type.setAlignment(Qt.AlignCenter)
        self.label_type.setStyleSheet("font-size: 20px;")

        # Label to display the timer countdown
        self.timer_label = QLabel(self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 30px;")

        # Button to start or stop the timer
        self.start_button = QPushButton(f"Start {label_text}", self)
        self.start_button.clicked.connect(self.toggle_timer)

        # Vertical layout for the TimerWidget
        layout = QVBoxLayout(self)
        layout.addWidget(self.label_type)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.start_button)

        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # Variables to track timer state
        self.timer_running = False
        self.paused = False
        self.start_time = None

        # Initialize the timer label with the initial duration
        self.update_timer_label()

    def toggle_timer(self):
        """Toggle between starting and stopping the timer."""
        if not self.timer_running:
            # Start the timer if not already running and the timer is not at 00:00
            if self.timer_label.text() != "00:00":
                if self.paused:
                    # If timer was paused, resume from the current remaining time
                    self.start_time = QTime.currentTime().addSecs(-self.duration + self.remaining_time())
                else:
                    # If timer was not paused, start from the initial duration
                    self.start_time = QTime.currentTime()
                self.timer.start(1000)  # Start the timer with a timeout of 1000 milliseconds (1 second)
                self.timer_running = True
                self.paused = False
                self.start_button.setText(f"Stop {self.label_type.text()}")
        else:
            # Stop the timer if it is running
            self.timer.stop()
            self.timer_running = False
            self.paused = True
            self.start_button.setText(f"Start {self.label_type.text()}")

    def update_timer(self):
        """Update the timer label based on elapsed time and switch timer if needed."""
        elapsed_time = self.start_time.elapsed() // 1000
        remaining_time = max(0, self.duration - elapsed_time)

        # Update the timer label with the remaining time
        self.timer_label.setText(self.format_time(remaining_time))

        # Check if timer reaches 00:00, then switch timer and toggle the timer state
        if remaining_time == 0:
            self.switch_tab_function()
            self.toggle_timer()

    def switch_timer(self, new_duration):
        """Switch to a new timer with a different duration."""
        self.duration = new_duration
        self.update_timer_label()

    def remaining_time(self):
        """Calculate and return the remaining time on the timer."""
        current_time = QTime.currentTime()
        elapsed_time = self.start_time.elapsed() // 1000
        return max(0, self.duration - elapsed_time)

    def update_timer_label(self):
        """Update the main timer label with the current duration."""
        self.timer_label.setText(self.format_time(self.duration))

    @staticmethod
    def format_time(seconds):
        """Format seconds into minutes:seconds."""
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

class PomodoroApp(QWidget):
    WORK_DURATION = 25 * 60
    BREAK_DURATION = 5 * 60

    def __init__(self):
        super().__init__()

        self.is_working = True

        # Create the main tab widget
        self.tab_widget = QTabWidget(self)

        # Create timer and to-do list tabs
        self.timer_tab = TimerWidget("Work Timer", self.WORK_DURATION, self.switch_to_rest_tab)
        self.rest_timer_tab = TimerWidget("Rest Timer", self.BREAK_DURATION, self.switch_to_work_tab)
        self.todo_tab = QWidget()

        # Initialize to-do list tab
        self.init_todo_tab()

        # Add tabs to the main tab widget
        self.tab_widget.addTab(self.timer_tab, "Work Timer")
        self.tab_widget.addTab(self.rest_timer_tab, "Rest Timer")
        self.tab_widget.addTab(self.todo_tab, "To-Do List")

        # Load tasks from the database
        self.load_tasks_from_database()

        # Main layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_widget)

        # Set the window title
        self.setWindowTitle("Pomodoro")

    def init_todo_tab(self):
        """Initialize the to-do list tab."""
        # Create a scroll area for the to-do list
        scroll_area = QScrollArea(self.todo_tab)
        scroll_area.setWidgetResizable(True)

        # Create a widget to contain the actual to-do list
        todo_list_container = QWidget()
        scroll_area.setWidget(todo_list_container)

        # Set up the layout for the to-do list container
        todo_list_layout = QVBoxLayout(todo_list_container)

        # Create the to-do list widget
        self.todo_list_widget = QListWidget()

        # Line edit for adding or editing tasks
        self.task_input = QLineEdit()

        # Buttons for task operations
        add_button = QPushButton("➕", self)
        add_button.setFixedSize(30, 30)  # Adjust the width and height as needed
        add_button.clicked.connect(self.add_task)

        delete_button = QPushButton("🗑️", self)
        delete_button.setFixedSize(30, 30)  # Adjust the width and height as needed
        delete_button.clicked.connect(self.delete_task)

        edit_button = QPushButton("🖋️", self)
        edit_button.setFixedSize(30, 30)  # Adjust the width and height as needed
        edit_button.clicked.connect(self.edit_task)

        move_up_button = QPushButton("⬆️", self)
        move_up_button.setFixedSize(30, 30)  # Adjust the width and height as needed
        move_up_button.clicked.connect(self.move_task_up)

        move_down_button = QPushButton("⬇️", self)
        move_down_button.setFixedSize(30, 30)  # Adjust the width and height as needed
        move_down_button.clicked.connect(self.move_task_down)

        # Horizontal layout for task input and buttons
        task_layout = QHBoxLayout()
        task_layout.addWidget(self.task_input)
        task_layout.addWidget(add_button)
        task_layout.addWidget(delete_button)
        task_layout.addWidget(edit_button)
        task_layout.addWidget(move_up_button)
        task_layout.addWidget(move_down_button)

        # Vertical layout for the to-do list container
        todo_list_layout.addWidget(self.todo_list_widget)
        todo_list_layout.addLayout(task_layout)

        # Set up the main layout for the to-do tab
        layout = QVBoxLayout(self.todo_tab)
        layout.addWidget(scroll_area)

    def add_task(self):
        """Add a task to the to-do list and save to the database."""
        task_text = self.task_input.text().strip()
        if task_text:
            self.todo_list_widget.addItem(task_text)
            self.task_input.clear()

            # Save tasks to the database
            self.save_tasks_to_database()

    def delete_task(self):
        """Delete the selected task from the to-do list and save to the database."""
        selected_item = self.todo_list_widget.currentItem()
        if selected_item:
            self.todo_list_widget.takeItem(self.todo_list_widget.row(selected_item))

            # Save tasks to the database
            self.save_tasks_to_database()

    def edit_task(self):
        """Edit the selected task in the to-do list and save to the database."""
        selected_item = self.todo_list_widget.currentItem()
        if selected_item:
            edited_text, ok_pressed = self.get_user_input("Edit Task", "Edit the task:", selected_item.text())
            if ok_pressed:
                selected_item.setText(edited_text)

                # Save tasks to the database
                self.save_tasks_to_database()

    def move_task_up(self):
        """Move the selected task up in the to-do list."""
        current_row = self.todo_list_widget.currentRow()
        if current_row > 0:
            item = self.todo_list_widget.takeItem(current_row)
            self.todo_list_widget.insertItem(current_row - 1, item)
            self.todo_list_widget.setCurrentRow(current_row - 1)
            self.save_tasks_to_database()

    def move_task_down(self):
        """Move the selected task down in the to-do list."""
        current_row = self.todo_list_widget.currentRow()
        if 0 <= current_row < self.todo_list_widget.count() - 1:
            item = self.todo_list_widget.takeItem(current_row)
            self.todo_list_widget.insertItem(current_row + 1, item)
            self.todo_list_widget.setCurrentRow(current_row + 1)
            self.save_tasks_to_database()

    def load_tasks_from_database(self):
        """Load tasks from the database and populate the to-do list."""
        try:
            connection = sqlite3.connect("todo_database.db")
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS tasks (task TEXT)")
            connection.commit()

            # Retrieve tasks from the database
            cursor.execute("SELECT task FROM tasks")
            tasks = cursor.fetchall()

            # Populate the to-do list
            for task in tasks:
                self.todo_list_widget.addItem(task[0])

        except sqlite3.Error as e:
            print(f"Error loading tasks from database: {e}")

        finally:
            if connection:
                connection.close()

    def save_tasks_to_database(self):
        """Save tasks from the to-do list to the database."""
        try:
            connection = sqlite3.connect("todo_database.db")
            cursor = connection.cursor()

            # Clear existing tasks in the database
            cursor.execute("DELETE FROM tasks")

            # Insert tasks from the to-do list
            for row in range(self.todo_list_widget.count()):
                task = self.todo_list_widget.item(row).text()
                cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task,))

            connection.commit()

        except sqlite3.Error as e:
            print(f"Error saving tasks to database: {e}")

        finally:
            if connection:
                connection.close()

    def switch_to_rest_tab(self):
        """Switch to the rest timer tab."""
        self.is_working = False
        self.tab_widget.setCurrentIndex(self.tab_widget.indexOf(self.rest_timer_tab))

    def switch_to_work_tab(self):
        """Switch to the work timer tab."""
        self.is_working = True
        self.tab_widget.setCurrentIndex(self.tab_widget.indexOf(self.timer_tab))

    def get_user_input(self, title, prompt, default_text=""):
        """Display a dialog to get user input."""
        text, ok_pressed = QInputDialog.getText(self, title, prompt, QLineEdit.Normal, default_text)
        return text, ok_pressed

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pomodoro_app = PomodoroApp()
    pomodoro_app.show()
    sys.exit(app.exec_())
