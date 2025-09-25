import os
import time
import json
import random
import uuid
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

TOPIC_NAME = "traffic_incidents"

# --- Simulation Data ---
INCIDENT_TYPES = ["accident", "road_closure", "heavy_traffic"]
LOCATIONS = [
    {"desc": "Brooklyn Bridge", "lat": 40.7061, "lon": -73.9969},
    {"desc": "Hollywood Blvd", "lat": 34.1016, "lon": -118.3331},
    {"desc": "I-5 & I-90 Interchange", "lat": 47.6000, "lon": -122.3297},
]

def get_traffic_incident():
    """Generates a random traffic incident."""
    location = random.choice(LOCATIONS)

    return {
        "incident_id": str(uuid.uuid4()),
        "type": random.choice(INCIDENT_TYPES),
        "latitude": location["lat"] + random.uniform(-0.01, 0.01),
        "longitude": location["lon"] + random.uniform(-0.01, 0.01),
        "severity": random.randint(1, 5),
        "description": f"Incident near {location['desc']}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result. """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} partition [{msg.partition()}]")

def main():
    """ Main function to produce traffic incident events. """
    kafka_config = get_kafka_config()
    producer = Producer(kafka_config)

    print(f"Producing traffic incidents to topic '{TOPIC_NAME}'. Press Ctrl-C to exit.")
    while True:
        try:
            incident_data = get_traffic_incident()

            producer.produce(
                TOPIC_NAME,
                key=incident_data["incident_id"],
                value=json.dumps(incident_data),
                callback=delivery_report
            )

            producer.flush()
            # Incidents are less frequent
            wait_time = random.randint(30, 90)
            print(f"--- Incident produced, waiting {wait_time}s ---")
            time.sleep(wait_time)

        except KeyboardInterrupt:
            print("\nShutting down producer...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()