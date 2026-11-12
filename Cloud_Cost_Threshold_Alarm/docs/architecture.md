
# Architecture

```text
Browser
  | HTTP / JSON
  v
Flask dashboard backend
  |-- Cost service ----> AWS Cost Explorer (optional; demo fallback)
  |-- Alert service ---> Local alert history + Amazon SNS (optional)
  |-- Device service --> AWS IoT Core MQTT publish (optional)
  |
  +---- JSON APIs ----> Dashboard cards, Chart.js, alert table, device panel

AWS IoT Core -- MQTT alert topic --> ESP32 firmware (separate firmware deliverable)
ESP32 -- heartbeat/status integration --> Device status service
```

The dashboard package implements the Flask APIs and frontend. Lambda/EventBridge scheduling and a continuously running MQTT status subscriber are separate deployment tasks and are not represented as completed by this local dashboard.
