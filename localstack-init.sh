#!/bin/bash
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
  --queue-url $DLQ_URL \
  --attribute-names QueueArn \
  --query 'Attributes.QueueArn' \
  --output text)

echo "DLQ ARN: $DLQ_ARN"

echo "Creating main SQS queue with redrive policy..."
QUEUE_URL=$(awslocal sqs create-queue \
  --queue-name notification-processing-queue \
  --attributes "RedrivePolicy={\"deadLetterTargetArn\":\"$DLQ_ARN\",\"maxReceiveCount\":\"3\"}" \
  --query 'QueueUrl' \
  --output text)

QUEUE_ARN=$(awslocal sqs get-queue-attributes \
  --queue-url $QUEUE_URL \
  --attribute-names QueueArn \
  --query 'Attributes.QueueArn' \
  --output text)

echo "Main Queue ARN: $QUEUE_ARN"

echo "Subscribing SQS queue to SNS topic..."
awslocal sns subscribe \
  --topic-arn $TOPIC_ARN \
  --protocol sqs \
  --notification-endpoint $QUEUE_ARN

echo "Setting SQS policy to allow SNS publishing..."
awslocal sqs set-queue-attributes \
  --queue-url $QUEUE_URL \
  --attributes "Policy={\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"sqs:SendMessage\",\"Resource\":\"$QUEUE_ARN\",\"Condition\":{\"ArnEquals\":{\"aws:SourceArn\":\"$TOPIC_ARN\"}}}]}"

echo "LocalStack SNS + SQS setup completed"
