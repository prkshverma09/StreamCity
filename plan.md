# StreamCity: Implementation Plan

This document breaks down the work required to build the StreamCity project, based on the `spec.md` design document.

## Phase 1: Foundational Setup (Confluent Cloud & Producers)

### Task 1.1: Configure Confluent Cloud
- **Description:** Set up a new environment and Kafka cluster in Confluent Cloud.
- **Actions:**
    - Create a new Confluent Cloud account if one doesn't exist.
    - Create a dedicated environment for StreamCity.
    - Provision a new Kafka cluster.
    - Generate API keys for connecting applications.
- **Acceptance Criteria:** API keys are securely stored and ready for use by producers and consumers.

### Task 1.2: Create Kafka Topics
- **Description:** Create the necessary Kafka topics as defined in the spec.
- **Actions:**
    - Using the Confluent Cloud UI or CLI, create the following topics:
        - `vehicle_locations`
        - `rider_tapped_on`
        - `traffic_incidents`
        - `surge_alerts` (for later use)
        - `delay_alerts` (for later use)
- **Acceptance Criteria:** All topics are created with default configurations.

### Task 1.3: Develop the Vehicle Location Producer
- **Description:** Create a Python script to simulate vehicle movements and publish them to the `vehicle_locations` topic.
- **Actions:**
    - Initialize a new Python project with a virtual environment.
    - Add `confluent-kafka-python` to `requirements.txt`.
    - Write a script (`producer_vehicle.py`) that:
        - Connects to Confluent Cloud using the API keys.
        - Simulates a fleet of 5-10 vehicles (buses/trains).
        - For each vehicle, periodically (e.g., every 5 seconds) generates new coordinates along a predefined simple path.
        - Publishes location updates to the `vehicle_locations` topic.
- **Acceptance Criteria:** Messages are successfully produced and can be viewed in the Confluent Cloud topic browser.

### Task 1.4: Develop Ancillary Producers
- **Description:** Create Python scripts to simulate rider taps and traffic incidents.
- **Actions:**
    - Create `producer_rider_taps.py` to send `rider_tapped_on` events at random intervals.
    - Create `producer_traffic.py` to send `traffic_incidents` events occasionally.
- **Acceptance Criteria:** Both producers can successfully send messages to their respective topics.

## Phase 2: Stream Processing with ksqlDB

### Task 2.1: Set up ksqlDB Application
- **Description:** Create and configure a ksqlDB application in Confluent Cloud.
- **Actions:**
    - Provision a new ksqlDB application.
    - Connect it to the existing Kafka cluster.
- **Acceptance Criteria:** ksqlDB editor is accessible and can query topics.

### Task 2.2: Implement Live Vehicle Tracking
- **Description:** Create ksqlDB streams and tables to track live vehicle locations.
- **Actions:**
    - Write a ksqlDB script (`ksql_setup.sql`) that:
        - Creates a `STREAM` on the `vehicle_locations` topic.
        - Creates a `TABLE` (`LIVE_VEHICLE_TABLE`) from the stream to store the latest location for each vehicle, using `GROUP BY vehicle_id`.
- **Acceptance Criteria:** A `SELECT * FROM LIVE_VEHICLE_TABLE;` query shows the most recent data for each vehicle.

### Task 2.3: Implement Surge Detection
- **Description:** Create a ksqlDB query to detect passenger surges.
- **Actions:**
    - Extend `ksql_setup.sql`:
        - Create a `STREAM` on the `rider_tapped_on` topic.
        - Write a windowed query that `GROUP`s by a geohash of the coordinates and `COUNT`s events in a 5-minute tumbling window.
        - Use a `HAVING` clause to filter for counts above a threshold.
        - `CREATE STREAM surge_alerts AS` the result of this query.
- **Acceptance Criteria:** When the rider tap producer generates a burst of events in one area, a corresponding message appears in the `surge_alerts` topic.

## Phase 3: Frontend Dashboard

### Task 3.1: Set up the Backend (WebSocket Server)
- **Description:** Create a Python-based web server to stream data to the frontend.
- **Actions:**
    - Initialize a new Python project (e.g., using FastAPI or Flask).
    - Add dependencies for Kafka (`confluent-kafka-python`) and WebSockets (`websockets`).
    - Write a Kafka consumer that subscribes to the changelog topic of `LIVE_VEHICLE_TABLE`.
    - Implement a WebSocket endpoint that, upon connection, pushes any message received from the Kafka consumer to the connected client.
- **Acceptance Criteria:** A simple WebSocket client can connect and receive live vehicle location updates.

### Task 3.2: Develop the Frontend Map
- **Description:** Create the web interface for the dashboard.
- **Actions:**
    - Set up a new frontend project (e.g., `npx create-react-app streamcity-ui`).
    - Add a mapping library (Leaflet or Mapbox).
    - Implement a component that:
        - Establishes a WebSocket connection to the backend server.
        - Initializes a map centered on a predefined city location.
        - On receiving a message, adds or updates a vehicle marker on the map.
- **Acceptance Criteria:** The map displays and updates vehicle icons in real-time as the vehicle producer runs.

### Task 3.3: Enhance the UI
- **Description:** Add filters and better visualizations.
- **Actions:**
    - Add UI controls to filter vehicles by type.
    - Use different icons for different vehicle types.
    - Display vehicle ID and passenger count on marker click.
    - Animate marker movements for a smoother user experience.
- **Acceptance Criteria:** The UI is interactive and user-friendly.

## Phase 4: Alerting and Finalizing

### Task 4.1: Implement the Alerting Service
- **Description:** Create a standalone service to send notifications.
- **Actions:**
    - Write a simple Python script (`alerter.py`).
    - The script will be a Kafka consumer subscribed to `surge_alerts` and `delay_alerts`.
    - On receiving a message, it will log the alert to the console (or integrate with a service like Slack via a webhook).
- **Acceptance Criteria:** Alerts generated by ksqlDB are printed to the console by the alerting service.

### Task 4.2: Implement Delay Alerts in ksqlDB
- **Description:** Create the ksqlDB logic for detecting vehicle delays. (This is more complex and scheduled for the end).
- **Actions:**
    - Pre-load route data into a `vehicle_routes` topic and create a ksqlDB `TABLE`.
    - Write a `STREAM-TABLE` join between `vehicle_locations` and `vehicle_routes`.
    - Implement logic (potentially a UDF) to calculate progress and delays.
    - Create the `delay_alerts` stream.
- **Acceptance Criteria:** A vehicle that is running behind its simulated schedule generates a message in the `delay_alerts` topic.

### Task 4.3: Documentation and Code Cleanup
- **Description:** Finalize the project documentation.
- **Actions:**
    - Create a `README.md` with instructions on how to set up and run the entire project.
    - Ensure all code is commented and follows a consistent style.
    - Store all API keys and sensitive configurations securely (e.g., using environment variables).
- **Acceptance Criteria:** A new developer can clone the repository and get the simulation running by following the README.