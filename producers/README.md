# StreamCity Producers

This directory contains the Python scripts that act as data producers for the StreamCity simulation. They generate events for vehicle locations, rider taps, and traffic incidents.

## Running the Producers

You can run these producers in two main ways:
1.  **Connected to a Local Kafka Instance** (Recommended for development)
2.  **Connected to Confluent Cloud**

### 1. Running with a Local Kafka Instance

This is the easiest way to get started.

**Prerequisites:**
*   Docker and Docker Compose installed.

**Steps:**

1.  **Start the Kafka Environment:**
    From the root directory of this project, run:
    ```bash
    docker-compose up -d
    ```
    This will start a Kafka broker and Zookeeper instance in the background. The Kafka broker will be accessible at `localhost:9092`.

2.  **Run a Producer:**
    Open a new terminal and run any of the producer scripts. For example, to start the vehicle location producer:
    ```bash
    python3 producers/producer_vehicle.py
    ```
    The script will automatically default to connecting to `localhost:9092` and start producing messages. You can run the other producers in separate terminals:
    ```bash
    python3 producers/producer_rider_taps.py
    ```
    ```bash
    python3 producers/producer_traffic.py
    ```

3.  **Stopping the Local Kafka:**
    When you're done, you can stop the local Kafka stack with:
    ```bash
    docker-compose down
    ```

### 2. Running with Confluent Cloud

To connect the producers to your Confluent Cloud cluster, you need to set the following environment variables.

**Prerequisites:**
*   A Confluent Cloud account with a running Kafka cluster.
*   API Key and Secret for your cluster.

**Steps:**

1.  **Set Environment Variables:**
    In your terminal, export the following variables, replacing the placeholder values with your actual Confluent Cloud credentials.

    ```bash
    # Confluent Cloud Bootstrap Server
    export KAFKA_BOOTSTRAP_SERVERS="pkc-xxxx.us-west-2.aws.confluent.cloud:9092"

    # Confluent Cloud API Key and Secret
    export KAFKA_API_KEY="YOUR_API_KEY"
    export KAFKA_API_SECRET="YOUR_API_SECRET"
    ```

2.  **Run a Producer:**
    Once the environment variables are set, you can run the producer scripts as before:
    ```bash
    python3 producers/producer_vehicle.py
    ```
    The scripts will detect the environment variables and automatically configure themselves to connect to Confluent Cloud using SASL_SSL.