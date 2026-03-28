import os
import pyttsx3
import pygetwindow as gw
import pyautogui
import time
import subprocess

class EnvironmentController:
    def __init__(self):
        self.engine = pyttsx3.init()

    def close_distracting_apps(self, window_title):
        # 🚨 Banned apps list
        banned_sites = ["instagram", "facebook", "chatgpt", "claude", "gemini", "grok", "google search", "new chat"]
        try:
            if any(site in window_title.lower() for site in banned_sites):
                windows = gw.getWindowsWithTitle(window_title)
                for win in windows:
                    try:
                        win.activate()
                        time.sleep(0.2)  
                        pyautogui.hotkey('ctrl', 'w') # Closes the tab
                    except Exception:
                        continue
        except Exception:
            pass

    def show_warning_popup(self, strike_count):
        """Spawns an independent OS process to guarantee the pop-up draws over Gradio."""
        if strike_count < 3:
            msg = f"⚠️ UNAUTHORIZED ACTIVITY DETECTED ⚠️\n\nThis is Warning {strike_count} of 3.\n\nYour unauthorized application has been force-closed. If you reach 3 warnings, your exam will be automatically suspended."
            title = f"Exam Proctor: Strike {strike_count}"
        else:
            msg = "🚨 MAXIMUM WARNINGS REACHED 🚨\n\nYour exam has been suspended due to repeated unauthorized activity. A full report is being generated for the administrator."
            title = "Exam Suspended"
        
        # We write a tiny, invisible Python script and execute it outside of Gradio
        script = f"""
import ctypes
msg = {repr(msg)}
title = {repr(title)}
# 0x40000 = Topmost, 0x30 = Warning Icon, 0x1000 = System Modal
ctypes.windll.user32.MessageBoxW(0, msg, title, 0x40000 | 0x30 | 0x1000)
"""
        # 0x08000000 is the Windows flag to hide the console window (CREATE_NO_WINDOW)
        subprocess.Popen(["python", "-c", script], creationflags=0x08000000)

    def trigger_study_mode(self):
        try:
            os.startfile('chrome.exe "https://unacademy.com/"')
        except Exception:
            os.system('start chrome "https://unacademy.com/"')

    def play_voice_alert(self, message):
        # Threading the voice using subprocess so it doesn't freeze the camera
        script = f"""
import pyttsx3
engine = pyttsx3.init()
engine.say({repr(message)})
engine.runAndWait()
"""
        subprocess.Popen(["python", "-c", script], creationflags=0x08000000)

# Standalone test
if __name__ == "__main__":
    test_controller = EnvironmentController()
    print("Testing isolated pop-up and voice...")
    test_controller.show_warning_popup(1)
    test_controller.play_voice_alert("Testing warning one.")