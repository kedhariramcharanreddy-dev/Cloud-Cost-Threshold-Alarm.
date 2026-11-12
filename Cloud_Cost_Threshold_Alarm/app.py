
from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
from datetime import datetime, timezone
import json, os
from services.cost_service import get_cost_summary
from services.alert_service import evaluate_status, create_alert, get_alerts, send_sns_notification
from services.device_service import get_device_status, publish_iot_alert

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config"
CONFIG.mkdir(exist_ok=True)
SETTINGS_FILE = CONFIG / "settings.json"
STATE_FILE = CONFIG / "state.json"

app = Flask(__name__, static_folder="frontend", static_url_path="")

DEFAULT_SETTINGS = {"monthly_budget": 100.0, "warning_percent": 80, "currency": "USD"}
DEFAULT_STATE = {"alerts": [], "device": {"connected": False, "last_seen": None, "last_status": "UNKNOWN"}}

def read_json(path, default):
    if not path.exists():
        write_json(path, default)
        return default.copy()
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default.copy()

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2))

def settings():
    return read_json(SETTINGS_FILE, DEFAULT_SETTINGS)

def state():
    return read_json(STATE_FILE, DEFAULT_STATE)

@app.get("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "mode": os.getenv("APP_MODE", "demo"), "timestamp": datetime.now(timezone.utc).isoformat()})

@app.get("/api/settings")
def get_settings():
    return jsonify(settings())

@app.post("/api/settings")
def update_settings():
    data = request.get_json(silent=True) or {}
    try:
        budget = float(data.get("monthly_budget"))
        warning = int(data.get("warning_percent"))
        if budget <= 0 or not 1 <= warning <= 99:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({"error": "Enter a budget greater than 0 and a warning percentage from 1 to 99."}), 400
    updated = {"monthly_budget": round(budget, 2), "warning_percent": warning, "currency": "USD"}
    write_json(SETTINGS_FILE, updated)
    return jsonify(updated)

@app.get("/api/costs")
def costs():
    s = settings()
    result = get_cost_summary()
    spend = float(result["monthly_spend"])
    status = evaluate_status(spend, s["monthly_budget"], s["warning_percent"])
    return jsonify({
        **result, "monthly_budget": s["monthly_budget"],
        "warning_threshold": round(s["monthly_budget"] * s["warning_percent"] / 100, 2),
        "remaining_budget": round(s["monthly_budget"] - spend, 2),
        "warning_percent": s["warning_percent"], "status": status
    })

@app.get("/api/alerts")
def alerts():
    return jsonify(get_alerts())

@app.get("/api/device/status")
def device_status():
    return jsonify(get_device_status())

@app.post("/api/test-alert")
def test_alert():
    data = request.get_json(silent=True) or {}
    status = data.get("status", "WARNING")
    if status not in ("WARNING", "OVER_BUDGET", "NORMAL"):
        return jsonify({"error": "Invalid alert status."}), 400
    s = settings()
    spend = s["monthly_budget"] * (s["warning_percent"] / 100 if status == "WARNING" else 1.05 if status == "OVER_BUDGET" else 0.25)
    alert = create_alert(status, spend, s["monthly_budget"], "Dashboard test alert")
    sns_result = send_sns_notification(alert)
    iot_result = publish_iot_alert(alert)
    return jsonify({"alert": alert, "sns": sns_result, "iot": iot_result})

@app.post("/api/device/heartbeat")
def device_heartbeat():
    # Optional endpoint for a device-side HTTP heartbeat or local testing.
    data = request.get_json(silent=True) or {}
    st = state()
    st["device"] = {
        "connected": True,
        "last_seen": datetime.now(timezone.utc).isoformat(),
        "last_status": data.get("status", "UNKNOWN")
    }
    write_json(STATE_FILE, st)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
