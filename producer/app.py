# producer/app.py
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

def send_message(channel, message_data):
    """Send message to RabbitMQ"""
    message = json.dumps(message_data)
    
    channel.basic_publish(
        exchange='task_exchange',
        routing_key='task.process',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
            content_type='application/json'
        )
    )
    
    print(f"Sent message: {message}")

def main():
    print("Starting Producer...")
    
    # Connect to RabbitMQ
    connection = connect_rabbitmq()
    channel = connection.channel()
    
    # Setup exchange and queue
    setup_exchange_and_queue(channel)
    
    # Send messages continuously
    message_count = 1
    try:
        while True:
            message_data = {
                'id': message_count,
                'task': f'Process task #{message_count}',
                'timestamp': datetime.now().isoformat(),
                'priority': 'normal' if message_count % 3 != 0 else 'high'
            }
            
            send_message(channel, message_data)
            message_count += 1
            
            # Wait 5 seconds before sending next message
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        connection.close()

if __name__ == '__main__':
    main()