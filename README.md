## Setting up RabbitMQ with Docker

### Step 1: Pull and Run RabbitMQ Container

```bash
# Pull RabbitMQ image with management plugin
docker pull rabbitmq:3-management

# Run RabbitMQ container
docker run -d \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=password \
  rabbitmq:3-management
```

### Step 2: Verify Installation

```bash
# Check if container is running
docker ps

# Check logs
docker logs rabbitmq
```

Access the management UI at `http://localhost:15672` (admin/password)

## Complete Lab Example

Let me create a comprehensive lab with producer and consumer applications:## Step-by-Step Lab Execution

### Step 1: Setup Project Structure
Create the directory structure and files as shown in the artifacts above.

### Step 2: Start RabbitMQ
```bash
# Start everything
docker-compose up --build

# Or start RabbitMQ first
docker-compose up rabbitmq -d
```

### Step 3: Verify RabbitMQ
- Access management UI: http://localhost:15672
- Login with admin/password
- Check that RabbitMQ is running

### Step 4: Start Producer and Consumer
```bash
# In separate terminals or use docker-compose
docker-compose up producer
docker-compose up consumer
```

### Step 5: Monitor the System
Watch the logs to see messages being produced and consumed:
```bash
docker-compose logs -f producer
docker-compose logs -f consumer
```

### Step 6: Experiment
Try these scenarios:
- Stop the consumer and watch messages queue up
- Scale consumers: `docker-compose up --scale consumer=3`
- Send priority messages through the management UI
- Monitor queue statistics in the web interface

## Key Learning Points

This lab demonstrates:
- **Message Persistence**: Messages survive RabbitMQ restarts
- **Acknowledgments**: Manual message acknowledgment for reliability
- **Load Balancing**: Multiple consumers share the workload
- **Priority Handling**: Different processing times based on message priority
- **Error Handling**: Connection retries and message requeuing
- **Monitoring**: Using the management UI to observe system behavior

The setup uses Docker Compose for easy orchestration and includes proper error handling, connection management, and monitoring capabilities.


# Project Structure

```
rabbitmq-lab/
├── docker-compose.yml
├── producer/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── consumer/
    ├── Dockerfile
    ├── requirements.txt
    └── app.py
```

# Setup Commands

# 1. Create project directory

```sh
mkdir rabbitmq-lab && cd rabbitmq-lab
```

# 2. Create subdirectories

```sh
mkdir producer consumer
```

# 3. Create all files (use the artifacts above)

# 4. Start the entire stack

```sh
docker-compose up --build
```

# Alternative: Run services separately

# Start RabbitMQ only

```sh
docker-compose up rabbitmq
```

# In separate terminals:

```sh
docker-compose up producer
docker-compose up consumer
```

# Useful Docker Commands

# View logs

```sh
docker-compose logs rabbitmq
docker-compose logs producer
docker-compose logs consumer
```

# Scale consumers (run multiple consumer instances)

```sh
docker-compose up --scale consumer=3
```

# Stop everything

```sh
docker-compose down
```

# Remove volumes (reset data)

```sh
docker-compose down -v
```

# Access RabbitMQ Management UI
# Open browser: http://localhost:15672
# Login: admin / password

# Monitor queue status

```sh
docker exec rabbitmq rabbitmqctl list_queues
```

# Monitor connections

```sh
docker exec rabbitmq rabbitmqctl list_connections
```

# Test with curl (alternative to producer)

```sh
curl -u admin:password \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{"properties":{},"routing_key":"task.process","payload":"{\"test\":\"message\"}","payload_encoding":"string"}' \
  http://localhost:15672/api/exchanges/%2F/task_exchange/publish
```
