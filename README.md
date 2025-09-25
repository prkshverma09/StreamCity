# StreamCity: A Real-Time Digital Twin 🏙️

StreamCity is a real-time data streaming application that simulates and visualizes a city's public transport system. It provides a live map of vehicle locations, detects operational anomalies like delays and passenger surges, and reports vehicle breakdowns. This system is designed to provide a "digital twin" of the city's transit network, offering real-time insights for operators and passengers.

## Project Structure

-   `spec.md`: The detailed design specification for the project.
-   `plan.md`: The implementation plan and task breakdown.
-   `producers/`: Contains Python scripts that simulate data (vehicles, riders, etc.) and send it to Kafka.
-   `ksql/`: Contains ksqlDB scripts for stream processing.
-   `dashboard_backend/`: Contains the FastAPI WebSocket server for the frontend.
-   `frontend/`: Contains the HTML, CSS, and JavaScript for the web dashboard.
-   `alerter/`: Contains the standalone consumer for surge alerts.
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

## Phase 3: Running the Dashboard Backend

This service provides a WebSocket endpoint that the future frontend can connect to for receiving live data. It consumes from the `LIVE_VEHICLE_TABLE` topic (created by the ksqlDB script) and broadcasts the updates.

**Prerequisites:**
-   Phases 1 and 2 are running.
-   The `LIVE_VEHICLE_TABLE` exists in ksqlDB and is being updated.

**Steps:**

1.  **Install Python Dependencies:**
    In a new terminal, install the required packages. It's recommended to use the same virtual environment as before.
    ```bash
    pip install -r dashboard_backend/requirements.txt
    ```

2.  **Run the Backend Server:**
    If you are using Confluent Cloud, make sure your Kafka environment variables are still set.
    ```bash
    uvicorn dashboard_backend.main:app --host 0.0.0.0 --port 8000
    ```
    The backend server is now running and will start consuming from Kafka and broadcasting to any connected WebSocket clients.

## Phase 4: Viewing the Live Dashboard

The frontend is a simple HTML page that uses Leaflet.js to display the vehicle data it receives from the backend's WebSocket.

**Prerequisites:**
-   Phases 1, 2, and 3 are all running.

**Steps:**

1.  **Serve the Frontend:**
    You cannot simply open the `index.html` file directly in the browser due to security policies (CORS). You need to serve it from a simple web server. The easiest way to do this is with Python. In a new terminal, run:
    ```bash
    python3 -m http.server --directory frontend 8080
    ```

2.  **Open the Dashboard:**
    Open your web browser and navigate to:
    [http://localhost:8080](http://localhost:8080)

    You should see a live map of New York City, and vehicle markers will appear and move in real-time as data is generated by your producers, processed by ksqlDB, and streamed through the backend.

## Phase 5: Running the Alerting Service

This is a standalone consumer that listens to the `surge_alerts` topic and logs a formatted message to the console whenever a surge is detected.

**Prerequisites:**
-   Phases 1 and 2 are running.
-   The `rider_tapped_on` producer is generating enough events in a concentrated area to trigger the surge detection logic in ksqlDB.

**Steps:**

1.  **Install Python Dependencies:**
    In a new terminal, install the required packages.
    ```bash
    pip install -r alerter/requirements.txt
    ```

2.  **Run the Alerter:**
    If you are using Confluent Cloud, make sure your Kafka environment variables are still set.
    ```bash
    python3 alerter/main.py
    ```
    The service will now be waiting. If a surge alert is produced by ksqlDB, you will see a formatted message printed in this terminal.

## Project Complete

All the core components of the StreamCity project as outlined in the initial plan are now complete! You have a full end-to-end pipeline: from data production, through stream processing, and out to both a real-time dashboard and a dedicated alerting service.