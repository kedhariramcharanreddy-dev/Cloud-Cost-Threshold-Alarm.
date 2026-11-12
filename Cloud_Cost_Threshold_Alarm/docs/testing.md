
# Testing checklist

Record the actual date, environment, evidence and result for each test. Do not mark PASS until it has been run.

| Test | Procedure | Expected result | Actual result |
|---|---|---|---|
| Dashboard startup | Run `python3 app.py` and open localhost | Dashboard loads | Not tested |
| Demo cost data | Keep `COST_SOURCE=demo` | Source badge says DEMO DATA | Not tested |
| Save budget | Set budget and warning percentage | Values persist after refresh | Not tested |
| Warning status | Configure spend/test alert to warning | WARNING status is displayed | Not tested |
| Over-budget status | Use over-budget test alert | OVER BUDGET status is displayed | Not tested |
| SNS | Configure topic and confirmed email | Email arrives | Not tested |
| IoT publish | Configure certificates and endpoint | Message appears on MQTT topic | Not tested |
| Device heartbeat | POST heartbeat endpoint | Device shows online temporarily | Not tested |
| Stale device | Wait more than 90 seconds | Device returns to offline | Not tested |
| AWS unavailable | Use invalid/unavailable AWS config | Clear unavailable/error state | Not tested |
