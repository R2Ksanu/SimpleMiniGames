import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# Function to create a gradient background on a canvas
def create_gradient(canvas, width, height, color1, color2):
    r1, g1, b1 = canvas.winfo_rgb(color1)
    r2, g2, b2 = canvas.winfo_rgb(color2)
    r1, g1, b1 = r1 // 256, g1 // 256, b1 // 256
    r2, g2, b2 = r2 // 256, g2 // 256, b2 // 256

    r_step = (r2 - r1) / height
    g_step = (g2 - g1) / height
    b_step = (b2 - b1) / height

    for y in range(height):
        r = int(r1 + r_step * y)
        g = int(g1 + g_step * y)
        b = int(b1 + b_step * y)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, y, width, y, fill=color)

# Function to change button color on hover
def on_enter_play(e):
    play_button.config(bg="#8B0000", fg="#FFFFFF")  # Dark red on hover

def on_leave_play(e):
    play_button.config(bg="#E6E6FA", fg="#00008B")  # Light purple with dark blue text

def on_enter_quit(e):
    quit_button.config(bg="#00008B", fg="#FFFFFF")  # Dark blue on hover

def on_leave_quit(e):
    quit_button.config(bg="#E6E6FA", fg="#8B0000")  # Light purple with dark red text

# Function to launch the selected game
def launch_game():
    choice = entry.get().strip()
    
    games = {
        "1": "CarGame/car_game.py",
        "2": "SnakeGame/snake_game.py",
        "3": "FlappyBird/flappy_bird.py"
    }
    
    if choice in games:
        game_path = os.path.join(os.path.dirname(__file__), games[choice])
        try:
            root.withdraw()
            result = subprocess.run(["python", game_path], check=False)
            if result.returncode == 0:
                root.deiconify()
                entry.delete(0, tk.END)
            else:
                root.destroy()
        except subprocess.CalledProcessError as e:
            root.deiconify()
            messagebox.showerror("Error", f"Failed to launch game {choice}. Make sure Python and Pygame are installed.")
        except FileNotFoundError:
            root.deiconify()
            messagebox.showerror("Error", f"Game file {game_path} not found.")
    else:
        messagebox.showwarning("Invalid Input", "Please enter 1, 2, or 3.")

# Function to quit the launcher
def quit_launcher():
    root.destroy()

# Set up the GUI
root = tk.Tk()
root.title("SMG-MiniGames Launcher")
root.geometry("400x500")
root.configure(bg="#FFFFFF")

# Create a canvas for the gradient background
canvas = tk.Canvas(root, width=400, height=500, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Create a gradient from pastel pink to pastel blue
create_gradient(canvas, 400, 500, "#FFB6C1", "#ADD8E6")

# Create a frame for the content with a white background
content_frame = tk.Frame(canvas, bg="#FFFFFF", bd=5, relief="raised")
content_frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=400)

# Title label with animation
title_label = tk.Label(content_frame, text="🎮 SMG-MiniGames 🎮", 
                       fg="#8B0000", bg="#FFFFFF", font=("Comic Sans MS", 20, "bold"))
title_label.pack(pady=20)

# Title color animation (dark red to dark blue)
colors = ["#8B0000", "#00008B"]
color_index = 0
def animate_title():
    global color_index
    title_label.config(fg=colors[color_index])
    color_index = (color_index + 1) % len(colors)
    root.after(500, animate_title)
animate_title()

# Border animation (pulsating between dark red and dark blue)
border_colors = ["#8B0000", "#00008B"]
border_index = 0
border_width = 3
def animate_border():
    global border_index, border_width
    canvas.delete("border")
    canvas.create_rectangle(50, 50, 350, 450, outline=border_colors[border_index], width=border_width, dash=(5, 5), tags="border")
    border_index = (border_index + 1) % len(border_colors)
    border_width = 3 if border_width == 5 else 5  # Pulsate between 3 and 5
    root.after(500, animate_border)
animate_border()

# Game selection labels (split for proper centering)
label1 = tk.Label(content_frame, text="Choose Your Game:", 
                  fg="#8B0000", bg="#FFFFFF", font=("Comic Sans MS", 14))
label1.pack(pady=5)
label2 = tk.Label(content_frame, text="[1] Car Game", 
                  fg="#00008B", bg="#FFFFFF", font=("Comic Sans MS", 14))
label2.pack(pady=5)
label3 = tk.Label(content_frame, text="[2] Snake Game", 
                  fg="#00008B", bg="#FFFFFF", font=("Comic Sans MS", 14))
label3.pack(pady=5)
label4 = tk.Label(content_frame, text="[3] Flappy Bird", 
                  fg="#00008B", bg="#FFFFFF", font=("Comic Sans MS", 14))
label4.pack(pady=5)

# Entry field with light purple background and animated border
entry = tk.Entry(content_frame, width=5, font=("Comic Sans MS", 16), justify="center", 
                 bg="#E6E6FA", fg="#8B0000", bd=3, relief="sunken")
entry.pack(pady=20)
entry.focus_set()  # Set focus to the entry field on startup

# Play button with light purple color and dark red hover effect
play_button = tk.Button(content_frame, text="Play", command=launch_game, 
                        bg="#E6E6FA", fg="#00008B", font=("Comic Sans MS", 14, "bold"), 
                        bd=3, relief="raised")
play_button.pack(pady=10)
play_button.bind("<Enter>", on_enter_play)
play_button.bind("<Leave>", on_leave_play)

# Quit button with light purple color and dark blue hover effect
quit_button = tk.Button(content_frame, text="Quit", command=quit_launcher, 
                        bg="#E6E6FA", fg="#8B0000", font=("Comic Sans MS", 14, "bold"), 
                        bd=3, relief="raised")
quit_button.pack(pady=10)
quit_button.bind("<Enter>", on_enter_quit)
quit_button.bind("<Leave>", on_leave_quit)

# Start the GUI
root.mainloop()