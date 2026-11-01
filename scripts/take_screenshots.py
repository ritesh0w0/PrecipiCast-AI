import subprocess
import time
import requests
import os

print("Starting Flask app...")
server = subprocess.Popen(["python", "app.py"])

try:
    ready = False
    for _ in range(20):
        try:
            r = requests.get("http://127.0.0.1:5000/health")
            if r.status_code == 200:
                ready = True
                print("Server is up and ready!")
                break
        except Exception:
            pass
        time.sleep(0.5)

    if not ready:
        print("Server failed to start in time.")
        exit(1)

    chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    dash_out = r"C:\rwh\assets\app_dashboard.png"
    pred_out = r"C:\rwh\assets\app_prediction_result.png"

    # 1. Dashboard screenshot
    cmd1 = f'"{chrome_exe}" --headless --window-size=1280,900 --screenshot={dash_out} http://127.0.0.1:5000'
    print("Capturing dashboard screenshot...")
    subprocess.run(f'cmd /c "{cmd1}"', shell=True, check=True)
    print("Dashboard captured!")

    # 2. Prediction result screenshot
    # Wait a bit for preview to submit and calculate
    cmd2 = f'"{chrome_exe}" --headless --virtual-time-budget=5000 --window-size=1280,900 --screenshot={pred_out} "http://127.0.0.1:5000/?preview=true"'
    print("Capturing prediction result screenshot...")
    subprocess.run(f'cmd /c "{cmd2}"', shell=True, check=True)
    print("Prediction result captured!")

finally:
    server.terminate()
    print("Flask server terminated.")
