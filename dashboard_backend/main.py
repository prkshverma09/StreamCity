import os
import json
import asyncio
import threading
from typing import List, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from confluent_kafka import Consumer, KafkaException

# --- FastAPI Application Setup ---
app = FastAPI()

# --- WebSocket Connection Management ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"New connection. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# --- Kafka Consumer Setup ---
def get_kafka_config():
    """Reads Kafka configuration from environment variables."""
    config = {
        'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        'group.id': 'dashboard-consumer-group-1',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': 'false'
    }
    if 'KAFKA_API_KEY' in os.environ and 'KAFKA_API_SECRET' in os.environ:
        config.update({
            'security.protocol': 'SASL_SSL',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': os.environ['KAFKA_API_KEY'],
            'sasl.password': os.environ['KAFKA_API_SECRET'],
        })
    return config

def kafka_consumer_job():
    """
    Runs in a background thread to consume from Kafka and broadcast to WebSockets.
    """
    kafka_config = get_kafka_config()
    consumer = Consumer(kafka_config)

    # The topic for a ksqlDB TABLE's changelog is the same as the table name.
    # ksqlDB creates topics in all caps by default.
    topic = "LIVE_VEHICLE_TABLE"
    consumer.subscribe([topic])
    print(f"Subscribed to Kafka topic: {topic}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            # The key is the vehicle_id, and the value is its latest state.
            vehicle_data = json.loads(msg.value().decode('utf-8'))
            print(f"Received from Kafka: {vehicle_data}")

            # Broadcast the message to all connected WebSocket clients
            broadcast_task = manager.broadcast(json.dumps(vehicle_data))
            loop.run_until_complete(broadcast_task)

        except KafkaException as e:
            print(f"Kafka error: {e}")
            continue
        except Exception as e:
            print(f"Error in consumer thread: {e}")
            continue

    consumer.close()

# --- FastAPI Endpoints ---
@app.on_event("startup")
async def startup_event():
    """On startup, start the Kafka consumer in a separate thread."""
    print("Starting Kafka consumer thread...")
    consumer_thread = threading.Thread(target=kafka_consumer_job, daemon=True)
    consumer_thread.start()

@app.get("/")
async def read_root():
    return {"message": "StreamCity Dashboard Backend is running. Connect to /ws for live data."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)