def validate_stream(active_window, face_conf_value):
    """Checks if the data from sensors is valid before processing."""
    # 1. Validate Active Window (Screen Agent Check)
    gr.validate(
        active_window and active_window != "None", 
        message="⚠️ Screen Agent: No Active Window Detected"
        # show_notif removed
    )
    # 2. Validate Face Detection (Vision Agent Check)
    gr.validate(
        face_conf_value > 50, 
        message="⚠️ Vision Agent: Poor Face Visibility"
        # show_notif removed
    )

# Refactored: Imports and background tracker management

import gradio as gr
import pandas as pd
import datetime
import threading
import time
import csv
from main import FocusTracker
from activity import ActivityTracker
from controller import EnvironmentController

history = []
focus_tracker = None
activity_tracker = None




# Controller state and timers (module-level globals)
focus_tracker_thread = None
last_plot_time = 0
window_history = []
low_focus_start_time = None
last_warning_time = 0
controller = EnvironmentController()
wasting_start_time = None
already_triggered = False
last_category = None

def start_background_trackers():
    global focus_tracker, activity_tracker, focus_tracker_thread
    if focus_tracker is None:
        focus_tracker = FocusTracker()
        focus_tracker.start()
    if activity_tracker is None:
        activity_tracker = ActivityTracker()

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
    global low_focus_start_time, last_warning_time
    global wasting_start_time, already_triggered, last_category
    global history, last_plot_time, window_history
    start_background_trackers()

    # 1. Get latest focus metrics
    focus_metrics = read_latest_focus_csv()
    focus_score = focus_metrics["Focus Score"]
    distracted_time = focus_metrics["Distracted Time"]
    face_conf = f"{focus_score}%"
    
    current_time = time.time()

    # --- 15-SECOND PERSISTENT WARNING LOGIC (unchanged) ---
    if focus_score < 50:
        if low_focus_start_time is None:
            # Start the timer when focus first drops
            low_focus_start_time = current_time
        # Check if 15 seconds have passed AND we haven't warned in the last 30 seconds
        elapsed_low_focus = current_time - low_focus_start_time
        if elapsed_low_focus >= 15 and (current_time - last_warning_time > 30):
            gr.Warning(f"⚠️ Focus has been low ({focus_score}%) for over 15 seconds!")
            last_warning_time = current_time 
    else:
        # Reset the timer if focus recovers
        low_focus_start_time = None
    # ------------------------------------------

    # 2. Get current window and category
    window_title, category = activity_tracker.get_current_status()

    # --- Decoupled Autonomous Focus Controller Logic ---
    # Track wasting app duration independently
    if category == "wasting":
        if last_category != "wasting":
            wasting_start_time = current_time
            already_triggered = False
        elif wasting_start_time is None:
            wasting_start_time = current_time
        elapsed_wasting = current_time - wasting_start_time if wasting_start_time else 0
        if elapsed_wasting > 20 and not already_triggered:
            controller.close_distracting_apps(window_title)
            controller.trigger_study_mode()
            controller.play_voice_alert()
            already_triggered = True
    else:
        # Reset wasting timer and trigger flag if not wasting
        wasting_start_time = None
        already_triggered = False
        # Reset distracted_time to 0 for non-wasting apps
        distracted_time = 0
    last_category = category
    # ----------------------------------------

    entry = {"Time": focus_metrics["Time"], "Window": window_title, "Category": category}
    window_history.append(entry)
    if len(window_history) > 20: window_history.pop(0)

    active_app = f"{window_title[:20]}... ({category})"
    productivity = focus_score
    # Show the reset distracted_time for non-wasting apps
    time_str = f"{distracted_time}s"

    # 3. Update history for graph
    if current_time - last_plot_time >= 3:
        history.append({"Time": focus_metrics["Time"], "Productivity": productivity, "App": category.capitalize()})
        if len(history) > 20: history.pop(0)
        last_plot_time = current_time

    return pd.DataFrame(history), active_app, face_conf, time_str

def format_window_history():
    if not window_history:
        return "<div style='color: gray;'>No activity yet...</div>"

    html = "<div style='font-family: monospace;'>"

    for entry in reversed(window_history[-10:]):  # show latest 10
        time_str = entry["Time"]
        window = entry["Window"][:30]
        category = entry["Category"].capitalize()

        color = "#22c55e" if category == "Coding" else "#f59e0b" if category == "Study" else "#ef4444"

        html += f"""
        <div style="
            display:flex;
            justify-content:space-between;
            padding:6px 10px;
            margin-bottom:5px;
            border-radius:8px;
            background:#111827;
            color:white;
        ">
            <span>🕒 {time_str}</span>
            <span>{window}</span>
            <span style="color:{color}; font-weight:bold;">{category}</span>
        </div>
        """

    html += "</div>"
    return html

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
            raw_log = gr.HTML(label="Live Activity Feed")

    timer = gr.Timer(1.0)
    timer.tick(
        fn=team_data_bridge,
        outputs=[plot, active_app, face_conf, total_time]
    )
    timer.tick(fn=format_window_history, outputs=raw_log)

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())