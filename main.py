
# Refactored into FocusTracker class
import cv2
import mediapipe as mp
import time
import csv
from datetime import datetime
import threading

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
        # Open CSV and write header if needed
        try:
            with open(self.csv_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Time", "Focus Score", "Reason", "Distracted Time"])
        except Exception:
            pass

        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
        cap = cv2.VideoCapture(0)

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
                    important_points = [
                        33, 160, 158, 133, 153, 144, # Left eye
                        362, 385, 387, 263, 373, 380, # Right eye
                        70, 63, 105, 66, 107, # Eyebrows
                        336, 296, 334, 293, 300,
                        1, 2, 98, 327 # Nose
                    ]
                    for idx in important_points:
                        x = int(face_landmarks.landmark[idx].x * w)
                        y = int(face_landmarks.landmark[idx].y * h)
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                    # Eye detection
                    left_eye_indices = [33, 160, 158, 133, 153, 144]
                    eye_points = []
                    for idx in left_eye_indices:
                        x = int(face_landmarks.landmark[idx].x * w)
                        y = int(face_landmarks.landmark[idx].y * h)
                        eye_points.append((x, y))
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                    eye_open = abs(eye_points[1][1] - eye_points[5][1])
                    if eye_open < 5:
                        focus_score -= 50
                        reason = "Eyes closed"

                    # Head/look direction
                    nose = face_landmarks.landmark[1]
                    nose_x = int(nose.x * w)
                    if nose_x < w * 0.35:
                        focus_score -= 50
                        reason = "Looking left"
                    elif nose_x > w * 0.65:
                        focus_score -= 50
                        reason = "Looking right"
            else:
                focus_score = 0
                reason = "No face detected"

            # Time-based distraction
            if focus_score < 50:
                if self._distracted_start is None:
                    self._distracted_start = time.time()
                distracted_time = int(time.time() - self._distracted_start)
            else:
                self._distracted_start = None
                distracted_time = 0

            # Autonomous action (not shown)
            # ...

            # Display (optional, comment out for headless)
            cv2.putText(frame, f"Focus Score: {focus_score}", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(frame, f"Reason: {reason}", (30, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Distracted Time: {distracted_time}s", (30, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            # cv2.putText(frame, f"Action: {action}", (30, 160),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
            # cv2.imshow("Focus Tracker AI", frame)

            # if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            #     break

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

        cap.release()
        cv2.destroyAllWindows()

# For standalone run
if __name__ == "__main__":
    tracker = FocusTracker()
    tracker.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tracker.stop()