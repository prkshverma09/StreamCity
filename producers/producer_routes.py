import os
import json
from confluent_kafka import Producer

def get_kafka_config():
    """
    Reads Kafka configuration from environment variables.
    Returns a dictionary of Kafka producer settings.
    """
    config = {
        'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    }

    if 'KAFKA_API_KEY' in os.environ and 'KAFKA_API_SECRET' in os.environ:
        config.update({
            'security.protocol': 'SASL_SSL',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': os.environ['KAFKA_API_KEY'],
            'sasl.password': os.environ['KAFKA_API_SECRET'],
        })
        print("Connecting to Confluent Cloud (SASL_SSL)")
    else:
        print("Connecting to local Kafka")

    return config

TOPIC_NAME = "vehicle_routes"

# --- Static Route Definitions ---
# This data will be pre-loaded into a Kafka topic so ksqlDB can use it as a TABLE.
ROUTES = {
    "route-bus-01": {
        "route_id": "route-bus-01",
        "vehicle_id": "bus-01", # To join with vehicle_locations
        "vehicle_type": "bus",
        "path": [
            [40.7128, -74.0060], # Downtown NYC
            [40.7306, -73.9969], # Greenwich Village
            [40.7580, -73.9855]  # Times Square
        ],
        "expected_travel_time_minutes": 25
    },
    "route-bus-02": {
        "route_id": "route-bus-02",
        "vehicle_id": "bus-02",
        "vehicle_type": "bus",
        "path": [
            [34.0522, -118.2437], # Downtown LA
            [34.0622, -118.2537],
            [34.0722, -118.2637],
            [34.0822, -118.2737]
        ],
        "expected_travel_time_minutes": 20
    },
    "route-train-A": {
        "route_id": "route-train-A",
        "vehicle_id": "train-A",
        "vehicle_type": "train",
        "path": [
            [40.7831, -73.9712], # Central Park
            [40.7580, -73.9855], # Times Square
            [40.7021, -74.0158]  # Wall Street
        ],
        "expected_travel_time_minutes": 15
    }
}

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result. """
    if err is not None:
        print(f"Message delivery failed for key {msg.key()}: {err}")
    else:
        print(f"Route '{msg.key().decode('utf-8')}' delivered to topic '{msg.topic()}'")

def main():
    """
    Main function to produce the static route data to Kafka.
    This script is intended to be run once to populate the topic.
    """
    kafka_config = get_kafka_config()
    producer = Producer(kafka_config)

    print(f"Publishing {len(ROUTES)} routes to topic '{TOPIC_NAME}'...")

    for route_id, route_data in ROUTES.items():
        producer.produce(
            TOPIC_NAME,
            key=str(route_id),
            value=json.dumps(route_data),
            callback=delivery_report
        )

    # Wait for all messages to be delivered
    outstanding_messages = producer.flush()
    if outstanding_messages > 0:
        print(f"Waiting for {outstanding_messages} outstanding messages to be delivered...")
    else:
        print("All messages flushed successfully.")

    print("Route data has been published.")

if __name__ == "__main__":
    main()