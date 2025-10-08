import subprocess
import sys
from tkinter import *
from tkinter import messagebox
import tkinter.font as tkFont

def run_sign_to_audio():
    try:
        subprocess.Popen([sys.executable, "finalsigntoaudio.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch Sign to Audio:\n{e}")

def run_audio_to_sign():
    try:
        subprocess.Popen([sys.executable, "finalaudiotosign.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch Audio to Sign:\n{e}")

def toggle_fullscreen(event=None):
    global fullscreen
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)
    # Update maximize/minimize button text accordingly
    if fullscreen:
        btn_fullscreen.config(text="Exit Fullscreen")
    else:
        btn_fullscreen.config(text="Fullscreen")

def minimize_window():
    root.iconify()

def maximize_window():
    root.state('zoomed')
    global fullscreen
    fullscreen = False
    btn_fullscreen.config(text="Fullscreen")

def animate_label_color():
    # Cycle through some vibrant colors in a loop
    global color_index
    colors = ['#ff4c4c', '#4cff4c', '#4c4cff', '#ff4cff', '#ffff4c', '#4cffff']
    color = colors[color_index % len(colors)]
    heading_label.config(fg=color)
    color_index += 1
    root.after(500, animate_label_color)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit the launcher?"):
        root.destroy()

fullscreen = False
color_index = 0

root = Tk()
root.title("Language Helper")
root.geometry("900x600")
root.minsize(600, 400)
root.config(bg="#222831")  # Dark background

# Custom fonts
heading_font = tkFont.Font(family="Helvetica", size=32, weight="bold")
subheading_font = tkFont.Font(family="Helvetica", size=18)
button_font = tkFont.Font(family="Helvetica", size=14, weight="bold")

# Heading Label with animated colors
heading_label = Label(root, text="Language Helper", font=heading_font, bg="#222831", fg="#ff4c4c")
heading_label.pack(pady=30)

# Subheading
Label(root, text="Choose Mode", font=subheading_font, bg="#222831", fg="#eeeeee").pack(pady=10)

# Buttons with styling
btn_audio_to_sign = Button(root, text="Audio to Sign", font=button_font, width=20, height=2,
                           bg="#393e46", fg="#eeeeee", activebackground="#00adb5", activeforeground="#222831",
                           relief=FLAT, command=run_audio_to_sign)
btn_audio_to_sign.pack(pady=15)

btn_sign_to_audio = Button(root, text="Sign to Audio", font=button_font, width=20, height=2,
                           bg="#393e46", fg="#eeeeee", activebackground="#00adb5", activeforeground="#222831",
                           relief=FLAT, command=run_sign_to_audio)
btn_sign_to_audio.pack(pady=15)

# Frame for window control buttons
control_frame = Frame(root, bg="#222831")
control_frame.pack(pady=20)

btn_minimize = Button(control_frame, text="Minimize", font=button_font,
                      bg="#00adb5", fg="#222831", activebackground="#eeeeee", activeforeground="#00adb5",
                      width=12, height=1, relief=FLAT, command=minimize_window)
btn_minimize.grid(row=0, column=0, padx=10)

btn_maximize = Button(control_frame, text="Maximize", font=button_font,
                      bg="#00adb5", fg="#222831", activebackground="#eeeeee", activeforeground="#00adb5",
                      width=12, height=1, relief=FLAT, command=maximize_window)
btn_maximize.grid(row=0, column=1, padx=10)

btn_fullscreen = Button(control_frame, text="Fullscreen", font=button_font,
                        bg="#00adb5", fg="#222831", activebackground="#eeeeee", activeforeground="#00adb5",
                        width=12, height=1, relief=FLAT, command=toggle_fullscreen)
btn_fullscreen.grid(row=0, column=2, padx=10)
root.protocol("WM_DELETE_WINDOW", on_closing)
# Animate heading label color
animate_label_color()
root.mainloop()

