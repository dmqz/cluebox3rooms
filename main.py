import gpiozero
import pygame
import time
import tkinter as tk
import json
import os
import signal
import sys

# Set up the GPIO pins for the buttons
buttons = {
    "room1": gpiozero.Button(17, pull_up=True, bounce_time=0.1),
    "room2": gpiozero.Button(27, pull_up=True, bounce_time=0.1),
    "room3": gpiozero.Button(22, pull_up=True, bounce_time=0.1)
}

# Initialize pygame mixer for sound playback
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

# Create a tkinter window for displaying text
root = tk.Tk()
root.title("Clue Box")

# Make the window full screen
root.update_idletasks()
root.attributes('-fullscreen', True)
root.configure(bg='black')

# Set up a label to display text on the screen
label = tk.Label(root, text="", font=("Helvetica", 48), fg="white", bg="black", justify="center", wraplength=root.winfo_screenwidth()-50)
label.pack(expand=True)

# Function to load clues from a configuration file (JSON)
def load_clues(config_file='config.json'):
    if not os.path.exists(config_file):
        print(f"Config file '{config_file}' not found.")
        return {}
    
    with open(config_file, 'r') as file:
        try:
            clues = json.load(file)
            return clues
        except json.JSONDecodeError:
            print(f"Error reading the config file '{config_file}'. Make sure it is valid JSON.")
            return {}

# Load the clues from the config file
clues = load_clues()

# Variables to track button presses
button_press_start_time = {"room1": None, "room2": None, "room3": None}
button_hold_duration = 3  # seconds for reset
reset_triggered = False
press_counts = {"room1": 0, "room2": 0, "room3": 0}

# Function to adjust font size dynamically
def adjust_font_size(event=None):
    font_size = int(min(root.winfo_width(), root.winfo_height()) / 10)
    label.config(font=("Helvetica", font_size), wraplength=root.winfo_width()-50)

# Function to reset the app
def reset_app():
    global reset_triggered, press_counts
    if not reset_triggered:
        print("Resetting the app...")
        label.config(text="")
        pygame.mixer.stop()
        press_counts = {"room1": 0, "room2": 0, "room3": 0}
        reset_triggered = True

# Function to smoothly transition between clues
def transition_to_clue(clue):
    label.config(text="")
    label.after(500, play_new_clue, clue)

# Function to play a new clue
def play_new_clue(clue):
    pygame.mixer.stop()
    try:
        sound = pygame.mixer.Sound(clue["sound"])
        sound.play()
    except pygame.error as e:
        print(f"Error loading sound {clue['sound']}: {e}")
    
    label.config(text=clue["text"])

# Button press handler
def on_button_pressed(room):
    global button_press_start_time, reset_triggered, press_counts
    button_press_start_time[room] = time.time()
    print(f"Button Pressed in {room}!")
    
    if room in clues and press_counts[room] < len(clues[room]):
        transition_to_clue(clues[room][press_counts[room]])
    else:
        print(f"No more clues available for {room}.")
        label.config(text="No more clues.")
    
    press_counts[room] += 1
    reset_triggered = False

# Check if the button is held
def check_button_hold():
    global button_press_start_time, reset_triggered
    for room, button in buttons.items():
        if button.is_pressed:
            if button_press_start_time[room] and (time.time() - button_press_start_time[room]) >= button_hold_duration:
                reset_app()
        else:
            button_press_start_time[room] = None
    
    root.after(100, check_button_hold)

# Function to safely exit when Escape key is pressed
def exit_program(event=None):
    print("Exiting Clue Box...")
    pygame.mixer.quit()
    root.destroy()
    sys.exit(0)

# Attach button events
for room, button in buttons.items():
    button.when_pressed = lambda room=room: on_button_pressed(room)

# Start checking button hold
root.after(100, check_button_hold)

# Adjust font size on window resize
root.bind('<Configure>', adjust_font_size)

# Bind the Escape key to quit the application
root.bind("<Escape>", exit_program)

# Run the Tkinter event loop
root.mainloop()
