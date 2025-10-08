import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import speech_recognition as sr
import pyttsx3

# Set working directory
os.chdir(r"C:\Users\Saifu\python project")
print("Working Directory:", os.getcwd())

# Main window
root = tk.Tk()
root.title("Audio ↔ Sign Language Translator")
root.geometry("1000x600")

# Left panel (Controls)
left_frame = tk.Frame(root, width=250, bg="lightblue")
left_frame.pack(side="left", fill="y")

tk.Label(left_frame, text="🎙️ Audio to Sign", font=("Arial", 14, "bold"), bg="lightblue").pack(pady=10)

# Right panel (Sign display)
right_frame = tk.Frame(root, width=750, bg="white")
right_frame.pack(side="right", fill="both", expand=True)

canvas = tk.Canvas(right_frame, bg="white")
scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="white")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Enable drag-to-scroll
def on_mouse_press(event):
    canvas.scan_mark(event.x, event.y)

def on_mouse_drag(event):
    canvas.scan_dragto(event.x, event.y, gain=1)

canvas.bind("<ButtonPress-1>", on_mouse_press)
canvas.bind("<B1-Motion>", on_mouse_drag)

# Image references
image_refs = []

def clear_display():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    image_refs.clear()

def display_signs(recognized_text):
    clear_display()
    words = recognized_text.strip().split()

    for row_index, word in enumerate(words):
        row_frame = tk.Frame(scrollable_frame, bg="white")
        row_frame.pack(anchor="w", pady=15)

        for char in word:
            if char.isalnum():
                folder_path = os.path.join("Indian", char.upper())
                if os.path.isdir(folder_path):
                    image_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]
                    if image_files:
                        img_path = os.path.join(folder_path, image_files[0])
                        try:
                            img = Image.open(img_path)
                            img = img.resize((120, 120))
                            img_tk = ImageTk.PhotoImage(img)
                            image_refs.append(img_tk)

                            char_frame = tk.Frame(row_frame, bg="white")
                            char_frame.pack(side="left", padx=15)

                            img_label = tk.Label(char_frame, image=img_tk, bg="white")
                            img_label.pack()

                            text_label = tk.Label(char_frame, text=char.upper(), bg="white", font=("Arial", 12, "bold"))
                            text_label.pack()
                        except Exception as e:
                            print(f"[ERROR] Loading image for {char}: {e}")
                else:
                    print(f"[ERROR] Folder not found: {folder_path}")

def recognize_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak now...")
        try:
            audio = recognizer.listen(source, timeout=5)
            print("🔍 Recognizing...")
            recognized_text = recognizer.recognize_google(audio)
            print(f"✅ Recognized: {recognized_text}")
            display_signs(recognized_text)
        except sr.WaitTimeoutError:
            messagebox.showerror("Timeout", "Listening timed out. Please try again.")
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Could not understand the audio.")
        except sr.RequestError as e:
            messagebox.showerror("API Error", f"Could not request results.\nError: {e}")

# Buttons for Audio → Sign
tk.Button(left_frame, text="Start Listening", font=("Arial", 12), command=recognize_audio, bg="green", fg="white").pack(pady=10)
tk.Button(left_frame, text="Clear Display", font=("Arial", 12), command=clear_display, bg="red", fg="white").pack(pady=5)

# --- Sign to Audio Section ---
tk.Label(left_frame, text="🖐️ Sign to Audio", font=("Arial", 14, "bold"), bg="lightblue").pack(pady=20)

sign_input_frame = tk.Frame(left_frame, bg="lightblue")
sign_input_frame.pack()

constructed_text = tk.StringVar()
constructed_text.set("")

def add_char(c):
    current = constructed_text.get()
    constructed_text.set(current + c)

def speak_text():
    engine = pyttsx3.init()
    engine.say(constructed_text.get())
    engine.runAndWait()

def clear_text():
    constructed_text.set("")

# Alphabet buttons
for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    btn = tk.Button(sign_input_frame, text=letter, width=3, command=lambda l=letter: add_char(l))
    btn.grid(row=i//6, column=i%6, padx=2, pady=2)

tk.Label(left_frame, textvariable=constructed_text, bg="lightblue", font=("Arial", 12)).pack(pady=10)
tk.Button(left_frame, text="🔊 Speak", command=speak_text, bg="purple", fg="white", font=("Arial", 12)).pack(pady=5)
tk.Button(left_frame, text="❌ Clear", command=clear_text, bg="gray", fg="white", font=("Arial", 12)).pack(pady=5)

# Run the app
root.mainloop()
