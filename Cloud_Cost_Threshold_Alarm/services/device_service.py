
import json, os
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = Path(__file__).resolve().parents[1] / "config" / "state.json"

def get_device_status():
    try:
        data = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
        device = data.get("device", {})
        last_seen = device.get("last_seen")
        connected = False
        if last_seen:
            try:
                seen = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
                connected = (datetime.now(timezone.utc) - seen).total_seconds() < 90
            except Exception:
                pass
        return {"connected": connected, "last_seen": last_seen, "last_status": device.get("last_status", "UNKNOWN")}
    except Exception:
        return {"connected": False, "last_seen": None, "last_status": "UNKNOWN"}

def publish_iot_alert(alert):
    endpoint = os.getenv("AWS_IOT_ENDPOINT")
    topic = os.getenv("AWS_IOT_TOPIC", "cloudcost/device/alert")
    cert = os.getenv("AWS_IOT_CERT")
    key = os.getenv("AWS_IOT_PRIVATE_KEY")
    ca = os.getenv("AWS_IOT_CA")
    if not all([endpoint, cert, key, ca]):
        return {"published": False, "message": "AWS IoT certificates/endpoint not configured."}
    try:
        from awscrt import mqtt
        from awsiot import mqtt_connection_builder
        import json as jsonlib, time
        connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint, cert_filepath=cert, pri_key_filepath=key,
            ca_filepath=ca, client_id=os.getenv("AWS_IOT_CLIENT_ID", "cloud-cost-dashboard"),
            clean_session=True, keep_alive_secs=30
        )
        connection.connect().result()
        connection.publish(topic=topic, payload=jsonlib.dumps(alert), qos=mqtt.QoS.AT_LEAST_ONCE)
        time.sleep(1)
        connection.disconnect().result()
        return {"published": True, "message": f"Published to {topic}"}
    except Exception as exc:
        return {"published": False, "message": str(exc)}
