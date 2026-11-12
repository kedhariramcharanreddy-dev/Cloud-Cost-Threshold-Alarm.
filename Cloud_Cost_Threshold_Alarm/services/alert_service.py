
import json, os
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parents[1] / "config" / "state.json"

def _read():
    if not STATE_FILE.exists():
        return {"alerts": [], "device": {"connected": False, "last_seen": None, "last_status": "UNKNOWN"}}
    try: return json.loads(STATE_FILE.read_text())
    except Exception: return {"alerts": [], "device": {"connected": False, "last_seen": None, "last_status": "UNKNOWN"}}

def _write(data):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2))

def evaluate_status(spend, budget, warning_percent):
    if spend >= budget: return "OVER_BUDGET"
    if spend >= budget * warning_percent / 100: return "WARNING"
    return "NORMAL"

def get_alerts():
    return _read().get("alerts", [])

def create_alert(status, spend, budget, message):
    data = _read()
    alert = {
        "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
        "status": status, "spend": round(spend, 2), "budget": round(budget, 2),
        "message": message, "timestamp": datetime.now(timezone.utc).isoformat()
    }
    data.setdefault("alerts", []).insert(0, alert)
    data["alerts"] = data["alerts"][:50]
    _write(data)
    return alert

def send_sns_notification(alert):
    topic = os.getenv("SNS_TOPIC_ARN")
    if not topic:
        return {"sent": False, "message": "SNS not configured; alert saved locally."}
    try:
        import boto3
        client = boto3.client("sns", region_name=os.getenv("AWS_REGION", "us-east-1"))
        client.publish(
            TopicArn=topic,
            Subject=f"Cloud Cost {alert['status']} Alert",
            Message=(f"Status: {alert['status']}\nSpend: ${alert['spend']:.2f}\n"
                     f"Budget: ${alert['budget']:.2f}\nTime: {alert['timestamp']}")
        )
        return {"sent": True, "message": "SNS publish request accepted."}
    except Exception as exc:
        return {"sent": False, "message": str(exc)}
