import boto3
import json
from .bedrock import ask

SYSTEM_PROMPT = """You are a senior DevOps engineer AI assistant with direct access to AWS account data.
You will be given real AWS account information and must answer questions accurately based on that data.
Be concise, specific, and actionable. Format your responses clearly."""

def get_aws_context() -> str:
    """Gather real AWS account data to give Claude context."""
    context = []
    ec2 = boto3.client("ec2", region_name="us-east-1")
    s3 = boto3.client("s3")
    ce = boto3.client("ce", region_name="us-east-1")

    # EC2 instances
    try:
        instances = ec2.describe_instances()
        inst_list = []
        for r in instances["Reservations"]:
            for i in r["Instances"]:
                name = next((t["Value"] for t in i.get("Tags", []) if t["Key"] == "Name"), "unnamed")
                inst_list.append(f"- {name} ({i['InstanceId']}): {i['InstanceType']}, {i['State']['Name']}")
        context.append("EC2 Instances:\n" + ("\n".join(inst_list) if inst_list else "None running"))
    except Exception as e:
        context.append(f"EC2: Unable to fetch ({e})")

    # S3 buckets
    try:
        buckets = s3.list_buckets()["Buckets"]
        bucket_list = [f"- {b['Name']}" for b in buckets]
        context.append("S3 Buckets:\n" + "\n".join(bucket_list))
    except Exception as e:
        context.append(f"S3: Unable to fetch ({e})")

    # Monthly cost
    try:
        from datetime import datetime, timedelta
        today = datetime.today()
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        cost = ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["BlendedCost"]
        )
        amount = cost["ResultsByTime"][0]["Total"]["BlendedCost"]["Amount"]
        context.append(f"Current Month AWS Spend: ${float(amount):.2f}")
    except Exception as e:
        context.append(f"Cost: Unable to fetch ({e})")

    return "\n\n".join(context)


def run(question: str) -> str:
    aws_context = get_aws_context()
    full_message = f"Here is my current AWS account data:\n\n{aws_context}\n\nQuestion: {question}"
    return ask(SYSTEM_PROMPT, full_message)
