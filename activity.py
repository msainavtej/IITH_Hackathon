
# Refactored into ActivityTracker class
import ctypes
import time

class ActivityTracker:
    def __init__(self):
        pass

    @staticmethod
    def get_active_window_title():
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value.strip()

    @staticmethod
    def classify_activity(window_title):
        title = window_title.lower()
        if "visual studio code" in title or "vscode" in title:
            return "coding"
        elif any(term in title for term in ["cmd", "powershell", "ubuntu", "kali"]):
            return "coding"
        elif "pycharm" in title:
            return "coding"
        elif "youtube" in title:
            return "youtube"
        elif any(term in title for term in ["instagram", "x.com", "twitter"]):
            return "wasting"
        elif any(term in title for term in ["netflix", "prime video"]):
            return "wasting"
        elif any(term in title for term in ["claude", "chatgpt"]):
            return "studying"
        elif any(term in title for term in ["gemini", "grok"]):
            return "studying"
        elif any(term in title for term in ["colab", "github", "stackoverflow"]):
            return "coding"
        elif title == "":
            return "unknown"
        else:
            return "browsing"

    def get_current_status(self):
        """
        Returns (window_title, category)
        """
        window_title = self.get_active_window_title()
        category = self.classify_activity(window_title)
        return window_title, category

# For standalone run
if __name__ == "__main__":
    tracker = ActivityTracker()
    print("Activity Tracker Started. Press Ctrl+C to stop.")
    try:
        while True:
            window_title, category = tracker.get_current_status()
            print(f"Window: {window_title} | Category: {category}")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopped")