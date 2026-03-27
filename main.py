import cv2
import mediapipe as mp
import time

import csv
from datetime import datetime

file = open("focus_data.csv", mode="w", newline="")
writer = csv.writer(file)

# Write header
writer.writerow(["Time", "Focus Score", "Reason", "Distracted Time"])

# Initialize MediaPipe
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

face_mesh = mp_face_mesh.FaceMesh(
    refine_landmarks=True,
    max_num_faces=1
)

# Start webcam
cap = cv2.VideoCapture(0)

# Timer for distraction
distracted_start = None

last_logged_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    # Flip for natural view
    frame = cv2.flip(frame, 1)

    # Convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame
    results = face_mesh.process(rgb_frame)

    focus_score = 100
    reason = "Focused"

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:

            # Draw face mesh
            # --------- DRAW ONLY KEY POINTS ---------

            # Important landmark indices
            important_points = [
                # Left eye
                33, 160, 158, 133, 153, 144,
                # Right eye
                362, 385, 387, 263, 373, 380,
                # Eyebrows
                70, 63, 105, 66, 107,
                336, 296, 334, 293, 300,
                # Nose
                1, 2, 98, 327
            ]

            for idx in important_points:
                x = int(face_landmarks.landmark[idx].x * w)
                y = int(face_landmarks.landmark[idx].y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            # --------- EYE DETECTION ---------
            left_eye_indices = [33, 160, 158, 133, 153, 144]

            eye_points = []
            for idx in left_eye_indices:
                x = int(face_landmarks.landmark[idx].x * w)
                y = int(face_landmarks.landmark[idx].y * h)
                eye_points.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            # Eye openness (vertical distance)
            eye_open = abs(eye_points[1][1] - eye_points[5][1])

            if eye_open < 5:
                focus_score -= 50
                reason = "Eyes closed"

            # --------- HEAD / LOOK DIRECTION ---------
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

    # --------- TIME-BASED DISTRACTION ---------
    if focus_score < 50:
        if distracted_start is None:
            distracted_start = time.time()
        distracted_time = int(time.time() - distracted_start)
    else:
        distracted_start = None
        distracted_time = 0

    # --------- AUTONOMOUS ACTION ---------
    if distracted_time > 3:
        action = "ALERT: Pay Attention!"
    else:
        action = "No action"

    # --------- DISPLAY ---------
    cv2.putText(frame, f"Focus Score: {focus_score}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.putText(frame, f"Reason: {reason}", (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.putText(frame, f"Distracted Time: {distracted_time}s", (30, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.putText(frame, f"Action: {action}", (30, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)

    cv2.imshow("Focus Tracker AI", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

    current_time = datetime.now().strftime("%H:%M:%S")

    if time.time() - last_logged_time > 1:
        writer.writerow([current_time, focus_score, reason, distracted_time])
        file.flush()
        last_logged_time = time.time()

cap.release()
cv2.destroyAllWindows()
file.close()