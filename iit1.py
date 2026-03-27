
# Refactored: Imports and background tracker management
import gradio as gr
import pandas as pd
import datetime
import threading
import time
import csv
from main import FocusTracker
from activity import ActivityTracker

# Global State
history = []
focus_tracker = None
activity_tracker = None
focus_tracker_thread = None
last_plot_time = 0

# Start background trackers only once
def start_background_trackers():
    global focus_tracker, activity_tracker, focus_tracker_thread
    if focus_tracker is None:
        focus_tracker = FocusTracker()
        focus_tracker.start()
    if activity_tracker is None:
        activity_tracker = ActivityTracker()

# Helper to read latest row from CSV
def read_latest_focus_csv(csv_path="focus_data.csv"):
    try:
        with open(csv_path, "r") as f:
            rows = list(csv.reader(f))
            if len(rows) > 1:
                last = rows[-1]
                return {
                    "Time": last[0],
                    "Focus Score": int(last[1]),
                    "Reason": last[2],
                    "Distracted Time": int(last[3])
                }
    except Exception:
        pass
    return {"Time": "--", "Focus Score": 0, "Reason": "No data", "Distracted Time": 0}

def team_data_bridge():
    # Ensure background trackers are running
    start_background_trackers()

    # 1. Get latest focus metrics from CSV
    focus_metrics = read_latest_focus_csv()
    focus_score = focus_metrics["Focus Score"]
    distracted_time = focus_metrics["Distracted Time"]
    face_conf = f"{focus_score}%"

    # 2. Get current window and category
    window_title, category = activity_tracker.get_current_status()
    active_app = f"{window_title[:20]}... ({category})"

    # 3. Productivity score = focus score
    productivity = focus_score

    # 4. Coding time (sum of all rows where category is 'coding')
    # For now, just show distracted_time as a placeholder for total time
    time_str = f"{distracted_time}s"

    # 5. Update history for graph (every 10 seconds only)
    global last_plot_time
    current_time = time.time()

    if current_time - last_plot_time >= 3:
        timestamp = focus_metrics["Time"]
        new_entry = {
            "Time": timestamp,
            "Productivity": productivity,
            "App": category.capitalize()
        }
        history.append(new_entry)
        if len(history) > 20:
            history.pop(0)
        last_plot_time = current_time

    df = pd.DataFrame(history)

    return df, active_app, face_conf, time_str

with gr.Blocks() as demo:
    gr.Markdown("# 🚀 Team Alpha: Autonomous Productivity Hub")

    with gr.Row():
        active_app = gr.Textbox(label="Active Window")
        face_conf = gr.Textbox(label="Focus Score (%)")
        total_time = gr.Label(label="Distracted Time (s)")

    with gr.Row():
        with gr.Column(scale=2):
            plot = gr.LinePlot(
                x="Time",
                y="Productivity",
                color="App",
                title="Real-Time Productivity Feed",
                y_lim=[0, 100]
            )
        with gr.Column(scale=1):
            gr.Markdown("### 🔍 Team Data Stream")
            raw_log = gr.JSON(label="Latest Packet")

    timer = gr.Timer(1.0)
    timer.tick(
        fn=team_data_bridge,
        outputs=[plot, active_app, face_conf, total_time]
    )
    timer.tick(fn=lambda: history[-1] if history else {}, outputs=raw_log)

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())