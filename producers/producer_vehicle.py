import os
import time
import json
import random
from confluent_kafka import Producer

def get_kafka_config():
    """
    Reads Kafka configuration from environment variables.
    Returns a dictionary of Kafka producer settings.
    """
    config = {
        'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
    }

    # Check for SASL (Confluent Cloud) credentials
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

TOPIC_NAME = "vehicle_locations"

# --- Vehicle Simulation ---
VEHICLES = {
    "bus-01": {"type": "bus", "route": [(40.7128, -74.0060), (40.7580, -73.9855)]}, # NYC
    "bus-02": {"type": "bus", "route": [(34.0522, -118.2437), (34.1522, -118.2537)]}, # LA
    "train-A": {"type": "train", "route": [(40.7831, -73.9712), (40.7021, -74.0158)]}, # NYC
}

def get_vehicle_location(vehicle_id):
    """Generates a new location for a vehicle along its route."""
    vehicle = VEHICLES[vehicle_id]
    # Simple simulation: move between two points
    lat = random.uniform(vehicle["route"][0][0], vehicle["route"][1][0])
    lon = random.uniform(vehicle["route"][0][1], vehicle["route"][1][1])

    return {
        "vehicle_id": vehicle_id,
        "type": vehicle["type"],
        "latitude": lat,
        "longitude": lon,
        "passenger_count": random.randint(5, 50),
        "status": "in_service",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result. """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} partition [{msg.partition()}] at offset {msg.offset()}")

def main():
    """ Main function to produce vehicle location events. """
    kafka_config = get_kafka_config()
    producer = Producer(kafka_config)

    print(f"Producing vehicle locations to topic '{TOPIC_NAME}'. Press Ctrl-C to exit.")
    while True:
        try:
            for vehicle_id in VEHICLES.keys():
                location_data = get_vehicle_location(vehicle_id)

                producer.produce(
                    TOPIC_NAME,
                    key=str(location_data["vehicle_id"]),
                    value=json.dumps(location_data),
                    callback=delivery_report
                )

            # Wait for any outstanding messages to be delivered and delivery reports to be received.
            producer.flush()
            print("--- Flushed batch, waiting 5s ---")
            time.sleep(5)

        except KeyboardInterrupt:
            print("\nShutting down producer...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10) # Wait before retrying

if __name__ == "__main__":
    main()