import gradio as gr
import pandas as pd
import datetime
import random
import pygetwindow as gw # For tracking active windows

# Global State
history = []
coding_seconds = 0
last_update_time = datetime.datetime.now()

def team_data_bridge():
    global coding_seconds, last_update_time
    
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%H:%M:%S")
    
    # 1. TRACK CODING TIME
    # Check if a coding app is in the foreground
    try:
        active_window = gw.getActiveWindow().title
    except:
        active_window = "None"
        
    is_coding = any(app in active_window for app in ["VS Code", "PyCharm", "main.py", "Sublime"])
    
    if is_coding:
        # Add the time elapsed since the last heartbeat
        delta = (current_time - last_update_time).total_seconds()
        coding_seconds += delta
    
    last_update_time = current_time
    
    # 2. MOCK TEAM DATA (Replace with your actual teammate imports)
    face_val = random.randint(75, 100) 
    app_score = 95 if is_coding else random.randint(10, 60)
    
    # Format coding time into MM:SS
    minutes, seconds = divmod(int(coding_seconds), 60)
    time_str = f"{minutes:02d}:{seconds:02d}"

    # 3. UPDATE HISTORY
    new_entry = {
        "Time": timestamp, 
        "Productivity": app_score,
        "App": "Coding" if is_coding else "Other"
    }
    history.append(new_entry)
    if len(history) > 20: history.pop(0)
    
    df = pd.DataFrame(history)
    
    # Return: (Graph, App Name, Face %, Status/Total Time)
    return df, active_window[:20] + "...", f"{face_val}%", time_str

with gr.Blocks() as demo:
    gr.Markdown("# 🚀 Team Alpha: Autonomous Productivity Hub")
    
    with gr.Row():
        # KPI CARDS
        active_app = gr.Textbox(label="Active Window")
        face_conf = gr.Textbox(label="Face Confidence")
        total_time = gr.Label(label="Total Coding Time (Session)")

    with gr.Row():
        with gr.Column(scale=2):
            # Gradio 6.0 NativePlot (Clean of old parameters)
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

    # HEARTBEAT: Set to 1.0 second for accurate time tracking
    timer = gr.Timer(1.0)
    timer.tick(
        fn=team_data_bridge, 
        outputs=[plot, active_app, face_conf, total_time]
    )
    
    # Sync the JSON log
    timer.tick(fn=lambda: history[-1] if history else {}, outputs=raw_log)

if __name__ == "__main__":
    # Theme moved to launch() for Gradio 6.0
    demo.launch(theme=gr.themes.Soft())