import asyncio
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import speech_recognition as sr
import pyttsx3
from g4f.client import Client
import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk

client = Client()

recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

root = tk.Tk()
root.title("Speech-to-Speech LLM Bot")
root.geometry("500x400")
root.configure(bg="#2C3E50")

style = ttk.Style()
style.configure("TLabel", background="#2C3E50", foreground="white", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 12), padding=6)
style.map("TButton", background=[("active", "#2980B9"), ("!active", "#1ABC9C")], foreground=[("!active", "white")])


text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10, bg="#ECF0F1", fg="black", font=("Helvetica", 12))
text_area.grid(column=0, row=0, padx=20, pady=20)

label_status = ttk.Label(root, text="Click the button and start speaking...")
label_status.grid(column=0, row=1, padx=10, pady=10)

def speak_text(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen_speech():
    with sr.Microphone() as source:
        label_status.config(text="Listening...")
        root.update()
        audio = recognizer.listen(source)
        
        try:
            label_status.config(text="Recognizing...")
            root.update()
            speech_text = recognizer.recognize_google(audio)
            text_area.insert(tk.END, f"You: {speech_text}\n")
            return speech_text
        except sr.UnknownValueError:
            label_status.config(text="Sorry, I could not understand the audio.")
            root.update()
            return None
        except sr.RequestError:
            label_status.config(text="Request to speech recognition service failed.")
            root.update()
            return None

def get_llm_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        if hasattr(response, 'choices') and len(response.choices) > 0:
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                return choice.message.content.strip()
            else:
                return "Message content not found in choice."
        else:
            return "No choices found in response."
    except Exception as e:
        return f"Error: {e}"

def process_speech():
    user_input = listen_speech()
    
    if user_input:
        llm_response = get_llm_response(user_input)
        
        if llm_response:
            text_area.insert(tk.END, f"Bot: {llm_response}\n")
            speak_text(llm_response)
        else:
            text_area.insert(tk.END, "Bot: Sorry, I couldn't generate a response.\n")
            
btn_speak = ttk.Button(root, text="Speak", command=process_speech)
btn_speak.grid(column=0, row=2, padx=10, pady=10)

root.mainloop()
