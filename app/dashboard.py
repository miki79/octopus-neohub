import asyncio
import threading
from flask import Flask, jsonify, render_template_string
from .control import state, control_loop
from .config import Config

app = Flask(__name__)

HTML = """
<!doctype html>
<title>Agile Thermostat Dashboard</title>
<h2>Agile Thermostat Status</h2>
<ul>
  <li><b>Device:</b> {{device}}</li>
  <li><b>Price:</b> {{state.last_price}} p/kWh</li>
  <li><b>Target Temp:</b> {{state.last_temp}} °C</li>
  <li><b>Manual Override:</b> {{state.manual_override}}</li>
  <li><b>Standby:</b> {{state.standby}}</li>
  <li><b>Preheat Active:</b> {{state.preheat_active}}</li>
  <li><b>Status:</b> {{state.status}}</li>
  <li><b>Last Update:</b> {{state.last_update}}</li>
</ul>
<a href="/json">JSON View</a>
"""

@app.route("/")
def index():
    return render_template_string(HTML, device=Config.DEVICE_NAME, state=state)

@app.route("/json")
def json_view():
    return jsonify(state)

def start():
    def run_control_loop():
        asyncio.run(control_loop())

    threading.Thread(target=run_control_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=Config.DASHBOARD_PORT)
