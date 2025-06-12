# consumer/app.py
import pika
import json
import time
import os
from datetime import datetime

def connect_rabbitmq():
    """Establish connection to RabbitMQ"""
    host = os.getenv('RABBITMQ_HOST', 'localhost')
    user = os.getenv('RABBITMQ_USER', 'admin')
    password = os.getenv('RABBITMQ_PASS', 'password')
    
    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(
        host=host,
        port=5672,
        virtual_host='/',
        credentials=credentials
    )
    
    # Retry connection
    max_retries = 30
    for i in range(max_retries):
        try:
            connection = pika.BlockingConnection(parameters)
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"Connection attempt {i+1}/{max_retries} failed. Retrying in 2 seconds...")
            time.sleep(2)
    
    raise Exception("Could not connect to RabbitMQ after maximum retries")

def setup_exchange_and_queue(channel):
    """Setup exchange and queue"""
    # Declare exchange
    channel.exchange_declare(
        exchange='task_exchange',
        exchange_type='direct',
        durable=True
    )
    
    # Declare queue
    channel.queue_declare(
        queue='task_queue',
        durable=True
    )
    
    # Bind queue to exchange
    channel.queue_bind(
        exchange='task_exchange',
        queue='task_queue',
        routing_key='task.process'
    )

def process_message(ch, method, properties, body):
    """Process received message"""
    try:
        # Parse message
        message_data = json.loads(body.decode('utf-8'))
        
        print(f"Received message: {message_data}")
        
        # Simulate processing time based on priority
        processing_time = 2 if message_data.get('priority') == 'high' else 5
        print(f"Processing task (will take {processing_time} seconds)...")
        
        time.sleep(processing_time)
        
        # Log completion
        print(f"✅ Completed task #{message_data['id']} at {datetime.now().isoformat()}")
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except json.JSONDecodeError:
        print("❌ Failed to decode message")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    print("Starting Consumer...")
    
    # Connect to RabbitMQ
    connection = connect_rabbitmq()
    channel = connection.channel()
    
    # Setup exchange and queue
    setup_exchange_and_queue(channel)
    
    # Set QoS to process one message at a time
    channel.basic_qos(prefetch_count=1)
    
    # Setup consumer
    channel.basic_consume(
        queue='task_queue',
        on_message_callback=process_message,
        auto_ack=False  # Manual acknowledgment
    )
    
    print("Waiting for messages. To exit press CTRL+C")
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nStopping consumer...")
        channel.stop_consuming()
        connection.close()

if __name__ == '__main__':
    main()