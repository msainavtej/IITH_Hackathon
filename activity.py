import ctypes
import time
from pynput import keyboard as kb

stop = False

def on_press(key):
    global stop
    try:
        if key.char == 'q':
            stop = True
    except AttributeError:
        pass

def get_active_window_title():
    # Uses built-in Windows API to get the active window title
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value.strip()

def classify_activity():
    window_title = get_active_window_title().lower()
    print(window_title)
    
    # Note: On Windows, browsers put the website name in the window title 
    # (e.g., "YouTube - Google Chrome"), so we don't need a separate URL grabber!
    
    if "visual studio code" in window_title or "vscode" in window_title:
        return "coding"
    elif "cmd" in window_title or "powershell" in window_title or "ubuntu" in window_title or "kali" in window_title:
        return "coding"
    elif "pycharm" in window_title:
        return "coding"
    elif "youtube" in window_title:
        return "youtube"
    elif "instagram" in window_title or "x.com" in window_title or "twitter" in window_title:
        return "wasting"
    elif "netflix" in window_title or "prime video" in window_title:
        return "wasting"
    elif "claude" in window_title or "chatgpt" in window_title:
        return "studying"
    elif "gemini" in window_title or "grok" in window_title:
        return "studying"
    elif "colab" in window_title or "github" in window_title or "stackoverflow" in window_title:
        return "coding"
    elif window_title == "":
        return "unknown"
    else:
        return "browsing"

def current_activity():
    print("Activity Tracker Started. Press 'q' to stop.")
    while not stop:
        activity = classify_activity()
        print(activity)
        time.sleep(10)
    print("Stopped")

if __name__ == "__main__":
    listener = kb.Listener(on_press=on_press)
    listener.start()
    current_activity()