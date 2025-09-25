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

TOPIC_NAME = "rider_tapped_on"

# --- Simulation Data ---
STATIONS = {
    "station-01": {"lat": 40.7128, "lon": -74.0060}, # Downtown NYC
    "station-02": {"lat": 40.7580, "lon": -73.9855}, # Times Square
    "station-03": {"lat": 34.0522, "lon": -118.2437}, # Downtown LA
}

def get_rider_tap():
    """Generates a random rider tap event."""
    station_id = random.choice(list(STATIONS.keys()))
    station = STATIONS[station_id]

    return {
        "event_id": str(uuid.uuid4()),
        "rider_id": f"rider-{random.randint(1000, 9999)}",
        "station_id": station_id,
        "latitude": station["lat"] + random.uniform(-0.001, 0.001),
        "longitude": station["lon"] + random.uniform(-0.001, 0.001),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result. """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} partition [{msg.partition()}]")

def main():
    """ Main function to produce rider tap events. """
    kafka_config = get_kafka_config()
    producer = Producer(kafka_config)

    print(f"Producing rider taps to topic '{TOPIC_NAME}'. Press Ctrl-C to exit.")
    while True:
        try:
            tap_data = get_rider_tap()

            producer.produce(
                TOPIC_NAME,
                key=tap_data["event_id"],
                value=json.dumps(tap_data),
                callback=delivery_report
            )

            producer.poll(0) # Serve delivery reports
            time.sleep(random.uniform(0.5, 3)) # Variable tap rate

        except KeyboardInterrupt:
            print("\nShutting down producer...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(10)

    producer.flush()

if __name__ == "__main__":
    main()