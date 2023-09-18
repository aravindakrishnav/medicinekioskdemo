import time
import tkinter as tk
import speech_recognition as sr
import threading
import queue
import pygame  # Import pygame for audio playback
import customtkinter as ctk

# Initialize pygame mixer
# from PIL import ImageTk, Image

pygame.mixer.init()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
# Create the main GUI window
root = ctk.CTk()
frame = ctk.CTkFrame(master=root)
frame.pack(pady=12, padx=10)
root.title("MediBot")

# Set the window size and make it non-resizable
root.geometry("600x400")
root.resizable(False, False)
root.eval('tk::PlaceWindow . center')

# Create a variable to store recognized text
recognized_text = tk.StringVar()
recognized_text.set("")

# Create a queue for passing recognized text between threads
text_queue = queue.Queue()

# Create a variable to track whether welcome message is playing
welcome_message_playing = True

# Create a variable to keep track of the recording thread
recording_thread = None

# Create a flag to control the recording thread
recording_thread_active = False

# Create a flag to track whether the "Start" button has been clicked
start_button_clicked = False

# Create a flag to track whether the confirmation audio has been played
confirmation_audio_played = False


# Function to play the welcome audio message
def play_welcome_message():
    global welcome_message_playing
    pygame.mixer.music.load("welcome_audio.mp3")
    pygame.mixer.music.play()
    welcome_message_playing = True


# Call the play_welcome_message function immediately
play_welcome_message()


# Function to start audio recording in a separate thread
def start_recording():
    global welcome_message_playing, recording_thread, recording_thread_active, start_button_clicked

    if welcome_message_playing:
        pygame.mixer.music.stop()  # Stop the welcome message playback
        welcome_message_playing = False

    if recording_thread is None or not recording_thread_active:
        recording_thread = threading.Thread(target=record_and_recognize)
        recording_thread.daemon = True  # Set the thread as daemon
        recording_thread.start()
        recording_thread_active = True

    # Set the flag to indicate that the "Start" button has been clicked
    start_button_clicked = True


# Function to record and recognize speech
def record_and_recognize():
    global recording_thread_active
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something...")
        try:
            while recording_thread_active:
                audio = recognizer.listen(source)
                try:
                    text = recognizer.recognize_google(audio)
                    text_queue.put(text)  # Put the recognized text in the queue
                    print(f"Recognized: {text}")  # Print recognized text to the console
                except sr.UnknownValueError:
                    text_queue.put("Speech recognition could not understand the audio.")
        except KeyboardInterrupt:
            pass


# Function to play confirmation audio after stopping recording
def play_confirmation_audio():
    global confirmation_audio_played
    if start_button_clicked and not confirmation_audio_played:
        confirmation_sound = pygame.mixer.Sound("please_wait.mp3")
        confirmation_sound.play()
        confirmation_audio_played = True


# Function to update recognized text in the main thread
def update_recognized_text():
    try:
        text = text_queue.get_nowait()  # Get text from the queue
        recognized_text.set(text)
        root.after(0, update_recognized_text)  # Continue listening for updates
    except queue.Empty:
        root.after(100, update_recognized_text)  # Retry after a short delay


# Function to stop audio recording
def stop_recording():
    global recording_thread_active
    recording_thread_active = False
    time.sleep(1)
    # Play confirmation audio
    play_confirmation_audio()


# Function to handle window closure
def on_closing():
    global recording_thread_active

    # Set the flag to stop the recording thread
    recording_thread_active = False
    root.destroy()


# Bind the window close event to the on_closing function
root.protocol("WM_DELETE_WINDOW", on_closing)

# Create and configure GUI buttons
start_button = ctk.CTkButton(master=frame, text="Start", command=start_recording)
stop_button = ctk.CTkButton(master=frame, text="Stop", command=stop_recording)
text_label = tk.Label(root, textvariable=recognized_text, width=40)  # Set a fixed width for the label

# Configure button placement using pack layout
frame.pack_configure(pady=150)
start_button.pack(side="top", padx=10, pady=10)
stop_button.pack(side="bottom", padx=10, pady=10)

# Start updating recognized text in the main thread
update_recognized_text()
root.mainloop()
