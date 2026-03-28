import os
import pyttsx3
import pygetwindow as gw
import pyautogui
import time
import subprocess

class EnvironmentController:
    def __init__(self):
        pass # Engine initialized in subprocess to prevent freezing

    def close_distracting_apps(self, window_title):
        banned_sites = ["instagram", "facebook", "chatgpt", "claude", "gemini", "grok", "google search", "new chat"]
        try:
            if any(site in window_title.lower() for site in banned_sites):
                windows = gw.getWindowsWithTitle(window_title)
                for win in windows:
                    try:
                        win.activate()
                        time.sleep(0.2)  
                        pyautogui.hotkey('ctrl', 'w') 
                    except Exception:
                        continue
        except Exception:
            pass

    def trigger_study_mode(self):
        try:
            os.startfile('chrome.exe "https://unacademy.com/"')
        except Exception:
            os.system('start chrome "https://unacademy.com/"')

    def play_voice_alert(self, message):
        script = f"""
import pyttsx3
engine = pyttsx3.init()
engine.say({repr(message)})
engine.runAndWait()
"""
        subprocess.Popen(["python", "-c", script], creationflags=0x08000000)