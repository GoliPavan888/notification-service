from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import boto3
import os

app = FastAPI(title="Notification Producer Service")

# SNS client (LocalStack compatible)
sns_client = boto3.client(
    "sns",
    endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
)

SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")


# -------- Request Schema --------
class NotificationRequest(BaseModel):
    recipientId: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1, description="email | sms | push")
    messageBody: str = Field(..., min_length=1)


# -------- API Endpoint --------
@app.post("/api/v1/notifications/publish", status_code=202)
def publish_notification(payload: NotificationRequest):
    if not SNS_TOPIC_ARN:
        raise HTTPException(status_code=500, detail="SNS topic not configured")

    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=payload.messageBody,
            MessageAttributes={
                "notificationType": {
                    "DataType": "String",
                    "StringValue": payload.type,
                },
                "recipientId": {
                    "DataType": "String",
                    "StringValue": payload.recipientId,
                },
            },
        )

        return {"message": "Notification accepted for processing"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
