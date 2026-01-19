# Notification Service (Event-Driven Architecture)

## 📌 Overview

This project implements a **production-style, event-driven notification system** using **AWS SNS and SQS**, fully emulated locally with **LocalStack** and orchestrated via **Docker Compose**.

The system demonstrates how modern backend services decouple producers and consumers using asynchronous messaging, retries, and Dead Letter Queues (DLQs)—patterns widely used by companies like Amazon, Stripe, and Netflix.

---

## 🏗️ Architecture

```
Client (REST API)
      |
      v
Producer Service (FastAPI)
      |
      v
SNS Topic (notification-events-topic)
      |
      v
SQS Queue (notification-processing-queue)
      |
      v
Consumer Service
      |
      v
DLQ (on failures after retries)
```

---

## ⚙️ Components

### 1️⃣ Producer Service

* Built with **FastAPI**
* Exposes a REST endpoint to publish notification events
* Publishes messages to **SNS**
* Stateless and horizontally scalable

**Endpoint:**

```
POST /api/v1/notifications/publish
```

**Sample Payload:**

```json
{
  "recipientId": "user-123",
  "type": "email",
  "messageBody": "Order shipped"
}
```

---

### 2️⃣ SNS (Simple Notification Service)

* Acts as an **event bus**
* Decouples producers from consumers
* Enables fan-out to multiple subscribers (future extensibility)

---

### 3️⃣ SQS Queue

* Receives messages from SNS
* Ensures **at-least-once delivery**
* Consumer polls messages asynchronously

---

### 4️⃣ Dead Letter Queue (DLQ)

* Configured using **RedrivePolicy**
* Messages are moved to DLQ after **3 failed processing attempts**
* Prevents message loss and infinite retries

---

### 5️⃣ Consumer Service

* Continuously polls SQS
* Processes notifications asynchronously
* Designed to be idempotent and fault-tolerant

---

## 🐳 Docker & LocalStack

* **Docker Compose** orchestrates all services
* **LocalStack** emulates AWS services locally (SNS, SQS)
* Infrastructure is initialized automatically using a startup script

### LocalStack Init Script Responsibilities

* Create SNS topic
* Create SQS queue and DLQ
* Attach RedrivePolicy
* Subscribe SQS to SNS
* Apply queue access policies

---

## 🚀 How to Run

### Prerequisites

* Docker
* Docker Compose
* PowerShell / Terminal

### Start the System

```
docker-compose up --build
```

---

## 🧪 Testing the Flow

### Publish a Notification

PowerShell example:

```
Invoke-RestMethod \
  -Uri http://localhost:8000/api/v1/notifications/publish \
  -Method POST \
  -ContentType "application/json" \
  -Body '{
    "recipientId": "user-123",
    "type": "email",
    "messageBody": "Order shipped"
  }'
```

### Expected Response

```
Notification accepted for processing
```

This confirms:

* API request accepted
* Message published to SNS
* Delivered to SQS
* Consumer is ready to process

---

## 🔐 Reliability & Best Practices

* Asynchronous communication
* Loose coupling between services
* DLQ for failure isolation
* Retry handling via SQS
* Containerized and reproducible setup

---

## 🧠 Key Learnings

* Event-driven system design
* AWS SNS + SQS integration
* Dead Letter Queue configuration
* Local AWS emulation using LocalStack
* Production-style async workflows

---

## 📈 Future Enhancements

* Multiple consumers (fan-out)
* Retry backoff strategies
* Metrics & monitoring (CloudWatch-style)
* Deployment to real AWS (ECS / Lambda)
* Authentication & authorization

---

## ✅ Conclusion

This project demonstrates a **real-world, production-ready async notification system** using AWS messaging patterns. It highlights scalability, reliability, and clean service boundaries—core principles of modern cloud-native architectures.
