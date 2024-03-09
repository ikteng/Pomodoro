# Pomodoro
Pomodoro 1 uses Tkinter, pygame, sqlite3, time and PIL
Pomodoro 2 uses sys, PyQt5, sqlite3

## Pomodoro Technique
The Pomodoro technique is a time management method that uses a timer to break down work into intervals of 25 minutes, separated by short breaks of 5 minutes.

## Database
The tasks.db stores all the remaining tasks left on the to-do list from the previous session when the program closes. The remaining tasks will be loaded onto the to-do list when a new session starts.

## Current Date and Time
There is a current date and time displayed on the top right corner which ticks every second.

## To-Do List
The to-do list in the middle allows user to add, delete, edit, strike-off tasks as well as move tasks up or down the list. There is an entry for users to type in their tasks.

## Audio Player
The audio player allows users to browse through their device and select an audio file to play. The audio player will dislpay the name of the audio file that is currently being played. It can be controlled by the play, pause and stop buttons at the bottom. There is also a rotating image of a disk as the audio plays.

## Pomodoro Timer
There are 2 timers (work timer and rest timer). The timer will count down from 25 mins and 5 mins respectively. When the timer is up, an alarm sound will play to alert the user for 5 secs or the user can stop the timer to stop the alarm. Then, the timer will be reset back to default.

## User Interface
The UI is created using Tkinter widgets, and the layout is organized using frames. The window includes a clock, date, to-do list, and audio player.

Note: The code references specific file paths, so it assumes the existence of certain files and directories. Adjustments may be needed based on the actual file structure.
