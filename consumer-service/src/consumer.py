import boto3
import os
import json
import time

# SQS client (LocalStack compatible)
sqs_client = boto3.client(
    "sqs",
    endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
)

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

# Simple in-memory idempotency store
processed_message_ids = set()


def process_message(message_id: str, body: str):
    if message_id in processed_message_ids:
        print(f"[IDEMPOTENT] Duplicate message ignored: {message_id}")
        return

    # Simulate sending notification
    print(f"[PROCESSING] Message ID: {message_id}")
    print(body)
    time.sleep(1)

    processed_message_ids.add(message_id)
    print(f"[SUCCESS] Processed message {message_id}")


def consume_messages():
    print("Consumer started. Waiting for messages...")

    while True:
        response = sqs_client.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        messages = response.get("Messages", [])

        for msg in messages:
            try:
                # SNS message is wrapped inside SQS
                sns_envelope = json.loads(msg["Body"])
                message_body = sns_envelope["Message"]
                message_id = msg["MessageId"]

                process_message(message_id, message_body)

                # Delete only after successful processing
                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=msg["ReceiptHandle"],
                )

            except Exception as e:
                print(f"[ERROR] Processing failed: {e}")
                # Message NOT deleted → retried → DLQ after maxReceiveCount

        time.sleep(2)


if __name__ == "__main__":
    consume_messages()
