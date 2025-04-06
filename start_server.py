import subprocess
import webbrowser
import time
import threading
import os

# Step 1: Run analysis.py (it will delete old and generate new graphs)
subprocess.run(['python', 'analysis.py'])

# Step 2: Start Python's built-in HTTP server
def start_server():
    os.chdir(".")  # Make sure you're in the root project folder
    subprocess.run(["python", "-m", "http.server", "8000"])

# Step 3: Open the browser after a short delay
def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:8000/frontend/index.html")

# Run both in parallel
threading.Thread(target=start_server).start()
open_browser()
