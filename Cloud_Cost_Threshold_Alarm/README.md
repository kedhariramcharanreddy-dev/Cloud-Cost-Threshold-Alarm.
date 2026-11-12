# Cloud Cost Threshold Alarm

## Project Overview
Cloud Cost Threshold Alarm is a cloud cost monitoring system designed to track AWS spending, monitor budget thresholds, and provide alerts when cloud expenditure approaches or exceeds the configured budget.

## Objectives
- Monitor cloud expenditure.
- Set monthly spending budgets.
- Configure warning thresholds.
- Display spending information through a web dashboard.
- Provide alerts for budget threshold conditions.
- Support IoT device status monitoring.

## Technologies Used
- Python
- Flask
- HTML, CSS and JavaScript
- AWS EC2
- AWS Cost Explorer
- AWS SNS
- AWS IoT Core
- ESP32

## Project Structure
```text
Cloud_Cost_Threshold_Alarm/
├── app.py
├── config/
├── docs/
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
├── services/
├── requirements.txt
└── README.md
```

## Dashboard
The web dashboard provides a visual interface for monitoring cloud spending, budget limits, warning thresholds, alerts, and device connection status.

## Deployment
The Flask application is deployed on an AWS EC2 instance.

**Live Dashboard:** http://34.224.218.171:5000

## Installation
1. Clone the repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Configure the required AWS settings and environment variables.
4. Run the application using `python app.py`.

## Author
kedhariramcharanreddy-dev
