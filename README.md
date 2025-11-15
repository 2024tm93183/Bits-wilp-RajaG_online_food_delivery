# Online Food Delivery - Full Project (Generated)

This project contains 6 FastAPI microservices with PostgreSQL per service, Redis for async events, docker-compose for local deployment, and Kubernetes manifests.

Quickstart:
1. Install Docker & Docker Compose
2. From this folder run: `docker-compose up --build`
3. Services accessible on ports 8001..8006.

Sample curl:
Create customer:
curl -X POST http://localhost:8001/v1/customers -H 'Content-Type: application/json' -d '{"name":"Alice","email":"a@example.com"}'

Place order (example):
curl -X POST http://localhost:8003/v1/orders -H 'Content-Type: application/json' -H 'Idempotency-Key: abc-123' -d '{"customer_id":1,"restaurant_id":1,"address_id":1,"items":[{"item_id":1,"quantity":1}],"payment_method":"card"}'
