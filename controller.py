
import os
import pyttsx3
import pygetwindow as gw
import pyautogui
import time

class EnvironmentController:
    def __init__(self):
        self.engine = pyttsx3.init()

    def close_distracting_apps(self, window_title):
        # Only close the specific tab/window if it's a distracting site (Instagram/Facebook)
        try:
            if any(site in window_title.lower() for site in ["instagram", "facebook"]):
                windows = gw.getWindowsWithTitle(window_title)
                for win in windows:
                    try:
                        win.activate()
                        time.sleep(0.2)  # Give time to focus
                        pyautogui.hotkey('ctrl', 'w')
                    except Exception:
                        # Ignore errors if window cannot be activated or closed
                        continue
        except Exception:
            # Ignore errors if window list cannot be fetched
            pass

    def trigger_study_mode(self):
        # Open Unacademy in Chrome
        try:
            os.startfile('chrome.exe "https://unacademy.com/"')
        except Exception:
            # Fallback: try with start command
            os.system('start chrome "https://unacademy.com/"')

    def play_voice_alert(self, message=None):
        if message is None:
            message = "You have been distracted. Redirecting you to study mode."
        self.engine.say(message)
        self.engine.runAndWait()
