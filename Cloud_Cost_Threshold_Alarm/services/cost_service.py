
import os
from datetime import date, timedelta

def get_cost_summary():
    """
    Demo mode returns clearly marked sample values.
    Set COST_SOURCE=aws and configure AWS credentials + Cost Explorer access
    to retrieve actual month-to-date spend.
    """
    if os.getenv("COST_SOURCE", "demo").lower() == "aws":
        try:
            import boto3
            today = date.today()
            start = today.replace(day=1).isoformat()
            end = (today + timedelta(days=1)).isoformat()
            client = boto3.client("ce", region_name=os.getenv("AWS_REGION", "us-east-1"))
            response = client.get_cost_and_usage(
                TimePeriod={"Start": start, "End": end},
                Granularity="DAILY",
                Metrics=["UnblendedCost"]
            )
            daily = []
            total = 0.0
            for item in response.get("ResultsByTime", []):
                amount = float(item["Total"]["UnblendedCost"]["Amount"])
                total += amount
                daily.append({"date": item["TimePeriod"]["Start"], "amount": round(amount, 2)})
            return {"monthly_spend": round(total, 2), "daily": daily, "source": "AWS Cost Explorer", "is_demo": False}
        except Exception as exc:
            return {"monthly_spend": 0.0, "daily": [], "source": "AWS unavailable: " + str(exc), "is_demo": False, "error": True}

    # Illustrative values only; not connected to an AWS account.
    today = date.today()
    daily = []
    for n in range(1, today.day + 1):
        d = today.replace(day=n)
        amount = round(1.2 + ((n * 7) % 13) * 0.42, 2)
        daily.append({"date": d.isoformat(), "amount": amount})
    total = round(sum(x["amount"] for x in daily), 2)
    return {"monthly_spend": total, "daily": daily, "source": "Demo sample data", "is_demo": True}
