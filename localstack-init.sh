#!/bin/sh
set -e

echo "Creating SNS topic..."
TOPIC_ARN=$(awslocal sns create-topic \
  --name notification-events-topic \
  --query 'TopicArn' \
  --output text)

echo "SNS Topic ARN: $TOPIC_ARN"

echo "Creating DLQ..."
DLQ_URL=$(awslocal sqs create-queue \
  --queue-name notification-processing-dlq \
  --query 'QueueUrl' \
  --output text)

DLQ_ARN=$(awslocal sqs get-queue-attributes \
  --queue-url "$DLQ_URL" \
  --attribute-names QueueArn \
  --query 'Attributes.QueueArn' \
  --output text)

echo "DLQ ARN: $DLQ_ARN"

echo "Creating attributes file for main queue..."
cat > /tmp/queue-attributes.json <<EOF
{
  "RedrivePolicy": "{\\"deadLetterTargetArn\\":\\"$DLQ_ARN\\",\\"maxReceiveCount\\":\\"3\\"}"
}
EOF

echo "Creating main SQS queue with RedrivePolicy..."
QUEUE_URL=$(awslocal sqs create-queue \
  --queue-name notification-processing-queue \
  --attributes file:///tmp/queue-attributes.json \
  --query 'QueueUrl' \
  --output text)

QUEUE_ARN=$(awslocal sqs get-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --attribute-names QueueArn \
  --query 'Attributes.QueueArn' \
  --output text)

echo "Queue ARN: $QUEUE_ARN"

echo "Subscribing SQS queue to SNS topic..."
awslocal sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol sqs \
  --notification-endpoint "$QUEUE_ARN"

echo "Setting SQS policy..."
cat > /tmp/sqs-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "$QUEUE_ARN",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "$TOPIC_ARN"
        }
      }
    }
  ]
}
EOF

awslocal sqs set-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --attributes Policy=file:///tmp/sqs-policy.json

echo "LocalStack SNS + SQS setup completed successfully"
