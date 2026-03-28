import cv2
import mediapipe as mp
import time
import csv
from datetime import datetime
import threading
import math

class FocusTracker:
    def __init__(self, csv_path="focus_data.csv"):
        self.csv_path = csv_path
        self.focus_score = 100
        self.reason = "Focused"
        self.distracted_time = 0
        self._distracted_start = None
        self._last_logged_time = 0
        self._latest_metrics = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Focus Score": 100,
            "Reason": "Focused",
            "Distracted Time": 0
        }
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def get_latest_metrics(self):
        """Return the latest focus metrics as a dict."""
        return self._latest_metrics.copy()

    def _run(self):
        try:
            with open(self.csv_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Time", "Focus Score", "Reason", "Distracted Time"])
        except Exception:
            pass

        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
        camera_url = "http://10.5.109.39:8080/video" 
        cap = cv2.VideoCapture(camera_url)

        try:
            while not self._stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    break

                h, w, _ = frame.shape
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb_frame)

                focus_score = 100
                reason = "Focused"

                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        left_eye_indices = [33, 160, 158, 133, 153, 144]
                        eye_points = []
                        for idx in left_eye_indices:
                            px = int(face_landmarks.landmark[idx].x * w)
                            py = int(face_landmarks.landmark[idx].y * h)
                            eye_points.append((px, py))
                            cv2.circle(frame, (px, py), 2, (0, 255, 0), -1)

                        v1 = math.hypot(eye_points[1][0] - eye_points[5][0], eye_points[1][1] - eye_points[5][1])
                        v2 = math.hypot(eye_points[2][0] - eye_points[4][0], eye_points[2][1] - eye_points[4][1])
                        h_dist = math.hypot(eye_points[0][0] - eye_points[3][0], eye_points[0][1] - eye_points[3][1])
                        
                        ear = (v1 + v2) / (2.0 * h_dist) if h_dist > 0 else 0

                        if ear < 0.20:
                            focus_score -= 50
                            reason = "Eyes closed"

                        all_x = [lm.x for lm in face_landmarks.landmark]
                        face_left = min(all_x)
                        face_right = max(all_x)
                        face_width = face_right - face_left
                        
                        nose_x = face_landmarks.landmark[1].x
                        
                        if face_width > 0:
                            gaze_ratio = (nose_x - face_left) / face_width
                            
                            if gaze_ratio < 0.35:
                                focus_score -= 50
                                reason = "Looking left"
                            elif gaze_ratio > 0.65:
                                focus_score -= 50
                                reason = "Looking right"
                else:
                    focus_score = 0
                    reason = "No face detected"

                if focus_score < 50:
                    if self._distracted_start is None:
                        self._distracted_start = time.time()
                    distracted_time = int(time.time() - self._distracted_start)
                else:
                    self._distracted_start = None
                    distracted_time = 0

                current_time = datetime.now().strftime("%H:%M:%S")
                if time.time() - self._last_logged_time > 1:
                    try:
                        with open(self.csv_path, mode="a", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow([current_time, focus_score, reason, distracted_time])
                    except Exception:
                        pass
                    self._last_logged_time = time.time()
                    self._latest_metrics = {
                        "Time": current_time,
                        "Focus Score": focus_score,
                        "Reason": reason,
                        "Distracted Time": distracted_time
                    }

        finally:
            cap.release()
            cv2.destroyAllWindows()
            if hasattr(face_mesh, 'close'):
                face_mesh.close()

if __name__ == "__main__":
    tracker = FocusTracker()
    tracker.start()
    print("Camera tracking started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tracker.stop()
        print("\nCamera tracking stopped.")
