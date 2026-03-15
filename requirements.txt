from flask import Flask
import threading
import time
import os

app = Flask(__name__)

def worker():
    while True:
        print("Agent is running...")
        time.sleep(10)

threading.Thread(target=worker).start()

@app.route("/")
def home():
    return "Agent Alive"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
