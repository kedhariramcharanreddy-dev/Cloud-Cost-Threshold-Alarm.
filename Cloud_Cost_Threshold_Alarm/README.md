
# Cloud Cost Threshold Alarm — Dashboard

A local Flask dashboard prototype for monitoring monthly AWS spend against a configurable budget. It includes a daily spending chart, budget settings, alert history, a device-status panel, and optional AWS Cost Explorer, SNS, and AWS IoT integrations.

## Important: demo mode vs live AWS

The project starts in **demo mode**. The displayed sample spending is illustrative and is not from an AWS account. The ESP32 status remains OFFLINE until a real heartbeat is received. Test alerts are saved locally; SNS and IoT publish only when their credentials/configuration are supplied.

## 1. Requirements

- Python 3.10+
- VS Code or another editor
- Internet connection for the Chart.js CDN and Google Fonts (dashboard still loads without the fonts; chart requires CDN access)
- Optional for live AWS: AWS account, IAM credentials/role, Cost Explorer access, SNS topic and AWS IoT certificates

## 2. Run on macOS

Open Terminal and move into this folder:

```bash
cd Cloud_Cost_Threshold_Alarm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 app.py
```

Open **http://127.0.0.1:5000** in Chrome.

Stop the server with `Control + C`.

## 3. Dashboard features

- Month-to-date spend, monthly budget, warning threshold and remaining budget
- Daily spend line chart
- Budget health indicator (NORMAL / WARNING / OVER_BUDGET)
- Editable budget and warning percentage (saved in `config/settings.json`)
- Test alert button and local alert history (`config/state.json`)
- ESP32 status based on a recent heartbeat; stale devices show OFFLINE
- Auto-refresh every 30 seconds

## 4. Enable AWS Cost Explorer (optional)

1. Enable Cost Explorer in the AWS Billing and Cost Management console if it is not already enabled.
2. Create/use an IAM identity with least-privilege permission for `ce:GetCostAndUsage`.
3. Configure AWS credentials using a role or the AWS CLI credential chain. Do not paste access keys into source code.
4. In `.env`, set:

```env
COST_SOURCE=aws
AWS_REGION=us-east-1
```

5. Restart Flask. Cost Explorer data can have a delay and is not necessarily real-time. The backend queries the current calendar month to date.

For local development, the AWS CLI profile can be configured with `aws configure`, but prefer temporary credentials or IAM roles where possible. Never commit credentials.

## 5. Enable SNS (optional)

Create an SNS topic, confirm the email subscription, and give the running identity permission to publish to that topic. Set `SNS_TOPIC_ARN` in `.env`. The Test alert button will attempt an SNS publish when configured.

## 6. Enable AWS IoT Core publishing (optional)

Create an AWS IoT Thing and device certificate, attach a restrictive IoT policy, and obtain the account-specific IoT data endpoint. Set the endpoint and local certificate paths in `.env`:

```env
AWS_IOT_ENDPOINT=your-endpoint-ats.iot.us-east-1.amazonaws.com
AWS_IOT_TOPIC=cloudcost/device/alert
AWS_IOT_CERT=/absolute/path/to/device-certificate.pem.crt
AWS_IOT_PRIVATE_KEY=/absolute/path/to/private.pem.key
AWS_IOT_CA=/absolute/path/to/AmazonRootCA1.pem
```

The Flask test-alert route publishes JSON to the configured topic. Keep private keys outside Git and restrict their file permissions. Do not use broad `iot:*` permissions in production.

## 7. ESP32 heartbeat

The dashboard does not claim the ESP32 is online by assumption. A device or local test client can send a heartbeat:

```bash
curl -X POST http://127.0.0.1:5000/api/device/heartbeat \\
  -H "Content-Type: application/json" \\
  -d '{"status":"NORMAL"}'
```

The device is considered online for 90 seconds after its last heartbeat. This HTTP endpoint is a development heartbeat; for the final MQTT implementation, have the backend/device status listener update the same state only after a real MQTT status message.

## 8. API endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Backend health |
| `/api/settings` | GET | Read budget settings |
| `/api/settings` | POST | Save budget settings |
| `/api/costs` | GET | Cost summary and threshold evaluation |
| `/api/alerts` | GET | Alert history |
| `/api/device/status` | GET | ESP32 status |
| `/api/test-alert` | POST | Create test alert; optionally publish SNS/IoT |
| `/api/device/heartbeat` | POST | Development heartbeat |

## 9. Project structure

```text
Cloud_Cost_Threshold_Alarm/
├── app.py
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/dashboard.js
├── services/
│   ├── cost_service.py
│   ├── alert_service.py
│   └── device_service.py
├── config/
│   ├── settings.json
│   └── state.json
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 10. Before project submission

- Replace demo mode with verified Cost Explorer data and take a screenshot showing the source.
- Test warning and over-budget values using controlled test data.
- Confirm SNS email delivery.
- Confirm MQTT publication in AWS IoT Core test client.
- Upload firmware and verify OLED, LED and buzzer behaviour.
- Test disconnection and stale heartbeat behaviour.
- Record only tests that were actually performed as PASS.
- Do not put AWS access keys, private keys or certificates in GitHub or report screenshots.

## Troubleshooting

- `python3: command not found`: install Python 3 from python.org or Homebrew.
- `ModuleNotFoundError: flask`: activate `venv` and run `pip install -r requirements.txt`.
- Port 5000 busy: run `PORT=5001 python3 app.py`, then open `http://127.0.0.1:5001`.
- AWS error: check Cost Explorer is enabled, IAM permissions, credentials and region. Cost Explorer is a billing API; its endpoint is global in behaviour, while the SDK region setting is commonly `us-east-1`.
