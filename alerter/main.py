import os
import json
from confluent_kafka import Consumer, KafkaException

def get_kafka_config():
    """Reads Kafka configuration from environment variables."""
    config = {
        'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        'group.id': 'alerter-consumer-group-1',
        'auto.offset.reset': 'earliest'
    }
    if 'KAFKA_API_KEY' in os.environ and 'KAFKA_API_SECRET' in os.environ:
        config.update({
            'security.protocol': 'SASL_SSL',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': os.environ['KAFKA_API_KEY'],
            'sasl.password': os.environ['KAFKA_API_SECRET'],
        })
    return config

def main():
    """
    Main function to consume from alert topics and print messages.
    """
    kafka_config = get_kafka_config()
    consumer = Consumer(kafka_config)

    topics = ["surge_alerts"] # Can be expanded to include "delay_alerts" later
    consumer.subscribe(topics)
    print(f"Alerter service subscribed to Kafka topics: {topics}")
    print("Waiting for alerts... Press Ctrl-C to exit.")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                alert_data = json.loads(msg.value().decode('utf-8'))

                # Simple console logging for the alert
                print("\n" + "="*30)
                print("🚨  S U R G E   A L E R T  🚨")
                print("="*30)
                print(f"  Geographic Zone (geohash): {alert_data.get('GEOHASH')}")
                print(f"  Number of Rider Taps: {alert_data.get('TAP_COUNT')}")
                print(f"  Time Window Start: {alert_data.get('WINDOW_START')}")
                print(f"  Time Window End: {alert_data.get('WINDOW_END')}")
                print("="*30 + "\n")

    except KeyboardInterrupt:
        print("\nShutting down alerter service...")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()