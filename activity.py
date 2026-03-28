import ctypes
import pygetwindow as gw
import time

class ActivityTracker:
    def __init__(self):
        pass

    @staticmethod
    def get_active_window_title():
        """Gets the window the user is currently clicking on."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value.strip()
        except Exception:
            return ""

    @staticmethod
    def scan_all_windows_for_cheating():
        """Scans ALL open windows on the computer, even in the background."""
        try:
            titles = gw.getAllTitles()
            for title in titles:
                title_lower = title.lower()
                # If a forbidden tab exists anywhere, return its exact title
                if any(term in title_lower for term in ["claude", "chatgpt", "new chat", "gemini", "grok", "google search"]):
                    return title 
        except Exception:
            pass
        return None

    def classify_activity(self, window_title):
        title = window_title.lower()
        
        # Whitelist the Gradio Dashboard
        if "gradio" in title or "127.0.0.1" in title or "localhost" in title:
            return "exam platform"
            
        elif "visual studio code" in title or "vscode" in title:
            return "allowed"
        elif any(term in title for term in ["cmd", "powershell", "ubuntu", "kali"]):
            return "allowed"
        elif "pycharm" in title:
            return "allowed"
        elif any(term in title for term in ["colab", "github", "stackoverflow"]):
            return "allowed"
            
        elif "youtube" in title:
            return "blocked"
        elif any(term in title for term in ["instagram", "facebook", "x.com", "twitter", "netflix", "prime video"]):
            return "blocked"
            
        elif title == "":
            return "unknown"
        else:
            return "browsing"

    def get_current_status(self):
        """
        Returns (window_title, category)
        """
        cheating_window = self.scan_all_windows_for_cheating()
        if cheating_window:
            return cheating_window, "blocked"
            
        window_title = self.get_active_window_title()
        category = self.classify_activity(window_title)
        return window_title, category

if __name__ == "__main__":
    tracker = ActivityTracker()
    print("Omniscient Activity Tracker Started. Press Ctrl+C to stop.")
    try:
        while True:
            window_title, category = tracker.get_current_status()
            print(f"Window: {window_title} | Category: {category}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopped")