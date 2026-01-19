import boto3
import os
import json
import time

sqs_client = boto3.client(
    "sqs",
    endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
)

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

processed_message_ids = set()


def wait_for_queue():
    while True:
        try:
            sqs_client.get_queue_attributes(
                QueueUrl=SQS_QUEUE_URL,
                AttributeNames=["QueueArn"]
            )
            print("SQS queue is available")
            return
        except Exception:
            print("Waiting for SQS queue...")
            time.sleep(3)


def process_message(message_id: str, body: str):
    if message_id in processed_message_ids:
        print(f"[IDEMPOTENT] Duplicate message ignored: {message_id}")
        return

    print(f"[PROCESSING] Message ID: {message_id}")
    print(body)
    time.sleep(1)

    processed_message_ids.add(message_id)
    print(f"[SUCCESS] Processed message {message_id}")


def consume_messages():
    print("Consumer started. Waiting for queue...")
    wait_for_queue()

    while True:
        response = sqs_client.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
        )

        messages = response.get("Messages", [])

        for msg in messages:
            try:
                sns_envelope = json.loads(msg["Body"])
                message_body = sns_envelope["Message"]
                message_id = msg["MessageId"]

                process_message(message_id, message_body)

                sqs_client.delete_message(
                    QueueUrl=SQS_QUEUE_URL,
                    ReceiptHandle=msg["ReceiptHandle"],
                )

            except Exception as e:
                print(f"[ERROR] Processing failed: {e}")

        time.sleep(2)


if __name__ == "__main__":
    consume_messages()
