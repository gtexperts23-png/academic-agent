from flask import Flask
import threading
import time

app = Flask(__name__)

def worker():
    while True:
        print("Agent is running...")
        time.sleep(10)

threading.Thread(target=worker).start()

@app.route("/")
def home():
    return "Agent Alive"
