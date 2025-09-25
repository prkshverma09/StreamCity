# StreamCity: A Real-Time Digital Twin 🏙️

StreamCity is a real-time data streaming application that simulates and visualizes a city's public transport system. It provides a live map of vehicle locations, detects operational anomalies like delays and passenger surges, and reports vehicle breakdowns. This system is designed to provide a "digital twin" of the city's transit network, offering real-time insights for operators and passengers.

## Project Structure

-   `spec.md`: The detailed design specification for the project.
-   `plan.md`: The implementation plan and task breakdown.
-   `producers/`: Contains Python scripts that simulate data (vehicles, riders, etc.) and send it to Kafka.
-   `ksql/`: Contains ksqlDB scripts for stream processing.
-   `docker-compose.yml`: A Docker Compose file to easily set up a local Kafka environment for development.

## Phase 1: Running the Data Producers

This phase covers how to get the data simulators running. You can connect them to a local Kafka instance or a managed Confluent Cloud cluster.

### Using a Local Kafka Instance (Recommended for Dev)

This method allows you to run the entire data pipeline on your local machine.

**Prerequisites:**
-   Docker
-   Docker Compose
-   Python 3.8+

**Steps:**

1.  **Start the Kafka Environment:**
    Open a terminal in the project root and run:
    ```bash
    docker-compose up -d
    ```
    This command will start a Zookeeper and a Kafka broker in the background. The Kafka broker will be available at `localhost:9092`.

2.  **Install Python Dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r producers/requirements.txt
    ```

3.  **Run the Producers:**
    Open separate terminal tabs for each producer script you want to run.

    *   **To simulate vehicle movements:**
        ```bash
        python3 producers/producer_vehicle.py
        ```
    *   **To simulate rider taps:**
        ```bash
        python3 producers/producer_rider_taps.py
        ```
    *   **To simulate traffic incidents:**
        ```bash
        python3 producers/producer_traffic.py
        ```

4.  **Shut Down the Environment:**
    When you are finished, you can stop the local Kafka stack with:
    ```bash
    docker-compose down
    ```

### Option 2: Connecting to Confluent Cloud

If you have a Confluent Cloud cluster, you can configure the producers to send data to it directly.

**Steps:**

1.  **Set Environment Variables:**
    Follow the instructions in the `producers/README.md` to set the necessary environment variables for your Confluent Cloud bootstrap server, API key, and secret.

2.  **Install Dependencies and Run Producers:**
    Follow steps 2 and 3 from the local setup guide. The producer scripts will automatically detect the environment variables and connect to Confluent Cloud.

## Next Steps

With the producers running, the next phase of the project involves:
## Phase 2: Processing Streams with ksqlDB

After setting up your producers and ensuring data is flowing into your Kafka topics (either locally or in Confluent Cloud), you can proceed with processing the streams.

**Prerequisites:**
-   A running ksqlDB cluster in Confluent Cloud.
-   Data being produced to the `vehicle_locations` and `rider_tapped_on` topics.

**Steps:**

1.  **Open the ksqlDB Editor:**
    In your Confluent Cloud dashboard, navigate to your ksqlDB cluster to open the web-based editor.

2.  **Run the SQL Scripts:**
    The logic for stream processing is located in the `ksql/` directory. You should run these scripts in the ksqlDB editor.

    *   **Live Vehicle Tracking:**
        -   Copy the entire content of `ksql/live_tracking.sql`.
        -   Paste it into the ksqlDB editor and run the query.
        -   This will create the `live_vehicle_table`, which always contains the latest status for every vehicle.

    *   **Surge Detection:**
        -   Copy the entire content of `ksql/surge_detection.sql`.
        -   Paste it into the ksqlDB editor and run the query.
        -   This will create the `surge_alerts` stream, which will receive new events whenever a passenger surge is detected.

## Next Steps

With the producers running and the ksqlDB queries active, the next phases of the project involve:
-   Building a **frontend dashboard** to visualize the data from `live_vehicle_table`.
-   Creating an **alerting service** to consume events from the `surge_alerts` topic.