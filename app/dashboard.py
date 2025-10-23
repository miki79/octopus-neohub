import asyncio
import logging
import threading
from flask import Flask, jsonify, render_template
from .control import state, control_loop
from .config import Config

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html", device=Config.DEVICE_NAME, state=state)

@app.route("/json")
def json_view():
    return jsonify(state)

def start():
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
        )

    def run_control_loop():
        asyncio.run(control_loop())

    threading.Thread(target=run_control_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=Config.DASHBOARD_PORT)
