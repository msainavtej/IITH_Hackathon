Autonomous Focus Intelligence System

An AI-powered system that monitors, analyzes, and autonomously improves user focus using computer vision, screen tracking, and real-time actions.

📌 Overview

The Autonomous Focus Intelligence System is designed to help users stay productive by detecting distractions and taking intelligent actions automatically.

Unlike traditional productivity tools that only track behavior, this system actively understands user attention and responds in real time—making it a step toward fully autonomous personal assistants.

⚡ Key Features

🎥 Real-Time Face Tracking
Uses computer vision to analyze eye movement, head position, and attention.

🖥️ Active Window Monitoring
Tracks current applications and maintains window usage history.

🧠 Focus Detection Engine
Combines visual data and screen activity to determine focus levels.

🤖 Autonomous Actions
Automatically reacts to distractions (e.g., closing or restricting apps).

📊 Focus Score & Insights
Provides real-time feedback and logs user productivity data.

🎛️ Interactive Dashboard
Built with Gradio for a clean and modern UI experience.


🏗️ System Architecture

The project consists of four main modules:

Computer Vision Module
Built using MediaPipe & OpenCV
Detects face, eyes, and head orientation
Activity Tracking Module
Tracks active windows and user activity
Maintains history of application usage
Decision Engine
Combines inputs from vision + activity tracking
Determines focus vs distraction
Automation Layer
Executes actions based on detected behavior
Enables true autonomy


🛠️ Tech Stack
Python
OpenCV
MediaPipe
Gradio


Threading & System APIs

▶️ How to Run

# Clone the repository
git clone https://github.com/msainavtej/IITH_Hackathon.git

# Navigate to project folder
cd your-repo-name

# Create virtual environment
python -m venv venv

# Activate environment
# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py


📂 Project Structure
├── main.py                # Main application entry point
├── activity.py            # Active window tracking
├── focus_tracker.py       # Focus detection logic
├── ui.py                  # Gradio interface
├── focus_data.csv         # Logged user data
├── requirements.txt
└── README.md


🎯 Use Cases
Students preparing for competitive exams (like JEE)
Remote workers and developers
Productivity-focused individuals
Smart study/work environments
To stop cheating in online exams


🚀 Future Improvements
Adaptive AI personalization based on user habits
Integration with browser extensions
Cross-device synchronization
Advanced distraction classification using ML models
Voice-based alerts and feedback


🤝 Team
Built during a hackathon by a team of 4:


Computer Vision Engineer
System Activity Tracking Engineer
UI Developers (2)


💡 What Makes It Unique?
Most tools track productivity.
This system acts on it.

By combining real-time perception + decision-making + execution, we move closer to a truly autonomous productivity assistant.By combining real-time perception + decision-making + execution, we move closer to a truly autonomous productivity assistant.

Main prototype exists in the final branch of repository.
