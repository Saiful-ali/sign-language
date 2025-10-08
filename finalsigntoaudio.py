import os
import logging

# Suppress TensorFlow INFO and WARNING messages including oneDNN and feedback manager warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0 = all logs, 1 = filter INFO, 2 = filter INFO and WARNING
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations to avoid related warnings

# Suppress absl logging
logging.getLogger('absl').setLevel(logging.ERROR)

# Import TensorFlow
import tensorflow as tf

# Import other libraries
import cv2
import numpy as np
import mediapipe as mp
import pyttsx3
import joblib
import time
import random
from keras.models import load_model
from tkinter import *
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageDraw, ImageFont


# Load trained model and label encoder
model = load_model("landmark_model.h5")
encoder = joblib.load("label_encoder.pkl")

# Text-to-speech setup
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Globals for recognition
last_pred_label = None
hold_start_time = None
hold_duration_required = 2  # seconds to hold steady
recognized = False

# OpenCV Video Capture
cap = cv2.VideoCapture(0)

running = False

def check_hands_inside_box(landmarks, box):
    x1, y1, x2, y2 = box
    for lm in landmarks:
        px, py = int(lm.x * frame_width), int(lm.y * frame_height)
        if px < x1 or px > x2 or py < y1 or py > y2:
            return False
    return True

def detect():
    global last_pred_label, hold_start_time, recognized, running

    if not running:
        return

    ret, frame = cap.read()
    if not ret:
        root.after(30, detect)
        return

    frame = cv2.flip(frame, 1)
    global frame_height, frame_width
    frame_height, frame_width = frame.shape[:2]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    x1, y1, x2, y2 = 30, 30, frame_width - 30, frame_height - 30

    landmarks_combined = []
    hands_in_box = True

    if result.multi_hand_landmarks:
        all_x = []
        all_y = []

        for hand_landmarks in result.multi_hand_landmarks:
            lm_points = []
            for lm in hand_landmarks.landmark:
                px, py = int(lm.x * frame_width), int(lm.y * frame_height)
                all_x.append(px)
                all_y.append(py)
                lm_points.append(lm)

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks_combined.append(lm_points)

        margin = 40
        x1 = max(min(all_x) - margin, 0)
        y1 = max(min(all_y) - margin, 0)
        x2 = min(max(all_x) + margin, frame_width)
        y2 = min(max(all_y) + margin, frame_height)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)

        for lm_points in landmarks_combined:
            if not check_hands_inside_box(lm_points, (x1, y1, x2, y2)):
                hands_in_box = False
                break

        if hands_in_box and len(landmarks_combined) in [1, 2]:
            combined_vals = []
            for lm_points in landmarks_combined:
                for lm in lm_points:
                    combined_vals.extend([lm.x, lm.y, lm.z])

            if len(landmarks_combined) == 1:
                combined_vals.extend([0.0]*63)

            input_data = np.array(combined_vals).reshape(1, -1)

            prediction = model.predict(input_data)
            confidence = np.max(prediction)
            pred_label = encoder.inverse_transform([np.argmax(prediction)])[0]

            current_time = time.time()

            if confidence > 0.6:
                if pred_label == last_pred_label:
                    if hold_start_time is None:
                        hold_start_time = current_time
                    elapsed = current_time - hold_start_time
                    if elapsed >= hold_duration_required and not recognized:
                        recognized = True
                        prediction_label.config(text=pred_label)
                        engine.say(pred_label)
                        engine.runAndWait()
                else:
                    last_pred_label = pred_label
                    hold_start_time = current_time
                    recognized = False

                if not recognized:
                    elapsed = time.time() - hold_start_time if hold_start_time else 0
                    cv2.putText(frame, f"Hold steady: {elapsed:.1f}/{hold_duration_required}s",
                                (10, frame_height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
                else:
                    cv2.putText(frame, f"Recognized: {pred_label}",
                                (10, frame_height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                hold_start_time = None
                recognized = False
                last_pred_label = None
                prediction_label.config(text="")
                cv2.putText(frame, "Low confidence - Hold sign properly",
                            (10, frame_height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        else:
            hold_start_time = None
            recognized = False
            last_pred_label = None
            prediction_label.config(text="")
            cv2.putText(frame, "Place hand(s) fully inside the yellow box",
                        (10, frame_height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    else:
        hold_start_time = None
        recognized = False
        last_pred_label = None
        prediction_label.config(text="")
        cv2.putText(frame, "Show hand(s) inside the yellow box",
                    (10, frame_height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(img)

    video_frame.imgtk = imgtk
    video_frame.config(image=imgtk)

    root.after(30, detect)  # ~30 fps

def clear_images():
    global image_labels
    for lbl in image_labels:
        lbl.destroy()
    image_labels.clear()

def show_sign_images(label_folder):
    global images_visible, image_labels

    # Toggle check
    if images_visible.get(label_folder, False):
        clear_images()
        images_visible[label_folder] = False
        info_label.config(text=f"Images for '{label_folder}' hidden.")
        return
    else:
        clear_images()  # clear any previous images

    folder_path = os.path.join("sign_images", label_folder)
    if not os.path.exists(folder_path):
        info_label.config(text=f"Folder '{folder_path}' does NOT exist!")
        print(f"Folder not found: {folder_path}")
        return

    image_files = [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        info_label.config(text=f"No image files found in folder '{label_folder}'!")
        print("No image files in folder.")
        return

    info_label.config(text=f"Showing images for '{label_folder}'")

    for i, file in enumerate(image_files):
        img_path = os.path.join(folder_path, file)
        try:
            img = Image.open(img_path)
            img = img.resize((150, 150), Image.Resampling.LANCZOS)  # Adjust size for better visibility
            imgtk = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image {img_path}: {e}")
            continue

        lbl = Label(images_display_frame, image=imgtk, bd=2, relief="raised", bg="#f0f0f0")
        lbl.image = imgtk
        lbl.grid(row=0, column=i, padx=5, pady=5)
        image_labels.append(lbl)

    images_visible[label_folder] = True

def random_color():
    # Generate bright pastel colors
    base = 150
    return f'#{random.randint(base,255):02x}{random.randint(base,255):02x}{random.randint(base,255):02x}'

def brighten_color(hex_color, amount=30):
    r = min(int(hex_color[1:3], 16) + amount, 255)
    g = min(int(hex_color[3:5], 16) + amount, 255)
    b = min(int(hex_color[5:7], 16) + amount, 255)
    return f'#{r:02x}{g:02x}{b:02x}'

def on_enter(event):
    btn = event.widget
    orig_color = btn._orig_bg
    bright_color = brighten_color(orig_color, 40)
    btn.config(bg=bright_color)

def on_leave(event):
    btn = event.widget
    btn.config(bg=btn._orig_bg)

def start_detection():
    global running
    if not running:
        running = True
        start_button.config(state=DISABLED, bg="#006400")
        stop_button.config(state=NORMAL, bg="#b22222")
        detect()

def stop_detection():
    global running
    running = False
    start_button.config(state=NORMAL, bg="#228B22")
    stop_button.config(state=DISABLED, bg="#b22222")

images_visible = {}  # To keep track of visibility per label folder
image_labels = []    # To keep references to image Label widgets

# ----------- Tkinter Setup and Styling --------------

root = Tk()
root.title("Sign Language Recognition")
root.state('zoomed')  # start maximized
root.resizable(True, True)

# Define fonts
title_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
prediction_font = tkfont.Font(family="Helvetica", size=36, weight="bold")
info_font = tkfont.Font(family="Helvetica", size=14)
button_font = tkfont.Font(family="Helvetica", size=14, weight="bold")

# Configure grid layout
root.grid_columnconfigure(0, weight=1)  # Left side for webcam
root.grid_columnconfigure(1, weight=1)  # Right side for prediction and images
root.grid_rowconfigure(0, weight=1)

# Left Frame for Webcam and Control buttons
left_frame = Frame(root, bg="#1e1e2f")
left_frame.grid(row=0, column=0, sticky='nsew')
left_frame.grid_rowconfigure(0, weight=1)
left_frame.grid_rowconfigure(1, weight=0)
left_frame.grid_columnconfigure(0, weight=1)

video_frame = Label(left_frame, bg="black", bd=4, relief="sunken")
video_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

# Control buttons frame below video
control_frame = Frame(left_frame, bg="#1e1e2f")
control_frame.grid(row=1, column=0, sticky='ew', pady=10)
control_frame.grid_columnconfigure(0, weight=1)
control_frame.grid_columnconfigure(1, weight=1)

start_button = Button(control_frame, text="Start Detection", command=start_detection,
                      font=button_font, bg="#228B22", fg="white", activeforeground="white",
                      relief="raised", bd=3, padx=25, pady=12, cursor="hand2")
start_button.grid(row=0, column=0, padx=20)
start_button._orig_bg = "#228B22"
start_button.bind("<Enter>", on_enter)
start_button.bind("<Leave>", on_leave)

stop_button = Button(control_frame, text="Stop Detection", command=stop_detection,
                     font=button_font, bg="#b22222", fg="white", state=DISABLED,
                     activeforeground="white", relief="raised", bd=3, padx=25, pady=12, cursor="hand2")
stop_button.grid(row=0, column=1, padx=20)
stop_button._orig_bg = "#b22222"
stop_button.bind("<Enter>", on_enter)
stop_button.bind("<Leave>", on_leave)

# Right Frame for Prediction and Images
right_frame = Frame(root, bg="#282c34")
right_frame.grid(row=0, column=1, sticky='nsew')
right_frame.grid_rowconfigure(0, weight=0)
right_frame.grid_rowconfigure(1, weight=0)
right_frame.grid_rowconfigure(2, weight=1)
right_frame.grid_columnconfigure(0, weight=1)

# Prediction Label and Info Label at the top right
Label(right_frame, text="Prediction:", font=title_font, fg="#61dafb", bg="#282c34").grid(row=0, column=0, pady=(15,5), sticky='n')
prediction_label = Label(right_frame, text="", font=prediction_font, fg="#50fa7b", bg="#282c34")
prediction_label.grid(row=1, column=0, pady=(0,15), sticky='n')
info_label = Label(right_frame, text="Show your hand(s) inside the yellow box.\nHold the sign steady for 3 seconds.",
                   font=info_font, fg="#c8ccd4", bg="#282c34", justify=LEFT)
info_label.grid(row=2, column=0, pady=(0,15), sticky='n')

# Images display frame below prediction (scrollable)
images_display_container = Frame(right_frame, bg="#44475a")
images_display_container.grid(row=3, column=0, sticky='nsew', padx=15, pady=10)
right_frame.grid_rowconfigure(3, weight=1)

# Scrollable canvas and scrollbar for images
images_canvas = Canvas(images_display_container, bg="#44475a", highlightthickness=0)
images_scrollbar = Scrollbar(images_display_container, orient=HORIZONTAL, command=images_canvas.xview)
images_canvas.configure(xscrollcommand=images_scrollbar.set)

images_scrollbar.pack(side=BOTTOM, fill=X)
images_canvas.pack(side=TOP, fill=BOTH, expand=True)

images_display_frame = Frame(images_canvas, bg="#44475a")
images_canvas.create_window((0,0), window=images_display_frame, anchor='nw')

def on_frame_configure(event):
    images_canvas.configure(scrollregion=images_canvas.bbox("all"))

images_display_frame.bind("<Configure>", on_frame_configure)

# Scrollable sign buttons frame under images frame
buttons_frame_container = Frame(right_frame, bg="#282c34")
buttons_frame_container.grid(row=4, column=0, sticky='ew', padx=10, pady=(0,15))
buttons_frame_container.grid_columnconfigure(0, weight=1)

buttons_canvas = Canvas(buttons_frame_container, height=75, bg="#282c34", highlightthickness=0)
buttons_canvas.grid(row=0, column=0, sticky='ew')

buttons_scrollbar = Scrollbar(buttons_frame_container, orient=HORIZONTAL, command=buttons_canvas.xview)
buttons_scrollbar.grid(row=1, column=0, sticky='ew')

buttons_canvas.configure(xscrollcommand=buttons_scrollbar.set)

buttons_frame = Frame(buttons_canvas, bg="#282c34")
buttons_canvas.create_window((0, 0), window=buttons_frame, anchor='nw')

def load_sign_buttons():
    folder_path = "sign_images"
    if not os.path.exists(folder_path):
        info_label.config(text="No 'sign_images' folder found.")
        return

    for widget in buttons_frame.winfo_children():
        widget.destroy()

    label_folders = sorted([f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))])

    if not label_folders:
        info_label.config(text="No sign label folders found inside 'sign_images'.")
        return

    colors = [random_color() for _ in label_folders]

    for idx, label_folder in enumerate(label_folders):
        bg_color = colors[idx]
        btn = Button(buttons_frame,
                     text=label_folder.replace("_", " ").title(),
                     bg=bg_color,
                     fg='white',
                     activeforeground='white',
                     font=button_font,
                     relief="raised",
                     bd=3,
                     padx=20,
                     pady=10,
                     cursor="hand2",
                     command=lambda l=label_folder: show_sign_images(l))
        btn._orig_bg = bg_color
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.pack(side="left", padx=10, pady=5)

    buttons_frame.update_idletasks()
    buttons_canvas.config(scrollregion=buttons_canvas.bbox("all"))

load_sign_buttons()

root.mainloop()

cap.release()
cv2.destroyAllWindows()
