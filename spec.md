# StreamCity: Real-Time Digital Twin - Design Specification

## 1. Overview

StreamCity is a real-time data streaming application that simulates and visualizes a city's public transport system. It provides a live map of vehicle locations, detects operational anomalies like delays and passenger surges, and reports vehicle breakdowns. This system is designed to provide a "digital twin" of the city's transit network, offering real-time insights for operators and passengers.

## 2. System Architecture

The architecture is based on a streaming data pipeline using Apache Kafka and Confluent Cloud. It consists of three main components:

*   **Producers:** Data simulators that generate events for vehicle movements, passenger interactions, and traffic incidents.
*   **Stream Processing:** A ksqlDB application on Confluent Cloud that processes, enriches, and analyzes the raw event streams to derive real-time insights.
*   **Consumers:** A web-based dashboard for visualization and a separate alerting service.

![System Architecture Diagram](https://i.imgur.com/3Z3gAm1.png)

### 2.1. Data Flow

1.  **Producers** publish events to Kafka topics in Confluent Cloud.
2.  **ksqlDB** consumes these events, performs transformations and aggregations, and writes the results to new Kafka topics.
3.  The **Web Dashboard** consumes processed data via a WebSocket connection to provide a real-time map visualization.
4.  The **Alerting Service** consumes anomaly events (e.g., delays, surges) and sends notifications.

## 3. Data Schemas (Kafka Topics)

All data will be in JSON format.

### 3.1. `vehicle_locations`

Contains the real-time geographic location and status of each vehicle.

*   **Key:** `vehicle_id` (string)
*   **Value:**
    *   `vehicle_id`: string (e.g., "bus-01")
    *   `type`: string ("bus", "train", "rideshare")
    *   `latitude`: float
    *   `longitude`: float
    *   `passenger_count`: integer
    *   `status`: string ("in_service", "broken_down", "end_of_service")
    *   `timestamp`: string (ISO 8601)

### 3.2. `rider_tapped_on`

Represents a passenger boarding a vehicle or entering a station.

*   **Key:** `event_id` (UUID string)
*   **Value:**
    *   `rider_id`: string
    *   `vehicle_id`: string (optional, for bus/train)
    *   `station_id`: string (optional, for train station)
    *   `latitude`: float
    *   `longitude`: float
    *   `timestamp`: string (ISO 8601)

### 3.3. `traffic_incidents`

Events representing traffic issues that could cause delays.

*   **Key:** `incident_id` (UUID string)
*   **Value:**
    *   `type`: string ("accident", "road_closure", "heavy_traffic")
    *   `latitude`: float
    *   `longitude`: float
    *   `severity`: integer (1-5)
    *   `description`: string
    *   `timestamp`: string (ISO 8601)

### 3.4. `vehicle_routes` (Static Table)

A static table defining the routes for each vehicle. This will be pre-loaded into a ksqlDB table.

*   **Key:** `route_id` (string)
*   **Value:**
    *   `route_id`: string
    *   `vehicle_type`: string ("bus", "train")
    *   `path`: array of `[latitude, longitude]` coordinates
    *   `expected_travel_time_minutes`: integer

## 4. Stream Processing (ksqlDB)

### 4.1. Live Vehicle Tracking

*   **Input:** `vehicle_locations` stream.
*   **Output:** A materialized view (`LIVE_VEHICLE_TABLE`) that stores the latest location and status for each `vehicle_id`. This table will be used to power the real-time map.

### 4.2. Surge Detection

*   **Input:** `rider_tapped_on` stream.
*   **Logic:**
    1.  Define geographic zones (geohashes or simple polygons).
    2.  Use a tumbling window (e.g., 5 minutes) to count `rider_tapped_on` events within each zone.
    3.  If the count exceeds a predefined threshold, emit an event to the `surge_alerts` topic.
*   **Output:** `surge_alerts` stream.

### 4.3. Delay Alerts

*   **Input:** `vehicle_locations` stream, `vehicle_routes` table.
*   **Logic:**
    1.  Join the `vehicle_locations` stream with the `vehicle_routes` table on `vehicle_id` (assuming a vehicle is tied to a route).
    2.  For each location update, calculate the vehicle's progress along its route.
    3.  Compare the actual time elapsed with the expected time to reach that point.
    4.  If the delay exceeds a threshold (e.g., 10 minutes), emit an event to the `delay_alerts` topic.
*   **Output:** `delay_alerts` stream.

## 5. Consumers

### 5.1. Web Dashboard

*   **Frontend:** A single-page application (SPA) using React or Vue.
*   **Map:** Leaflet or Mapbox GL JS for rendering the map and vehicle markers.
*   **Real-time Layer:** A WebSocket server will be created. A Kafka consumer will read from the `LIVE_VEHICLE_TABLE`'s changelog topic and push updates to connected web clients via WebSockets. The frontend will update vehicle positions based on these messages.
*   **Features:**
    *   Display all active vehicles on the map.
    *   Animate vehicle movements smoothly.
    *   Display alerts (surges, delays) on the map.
    *   Allow filtering by vehicle type.

### 5.2. Alerting Service

*   **Logic:** A standalone consumer application (e.g., a Python script).
*   **Functionality:**
    *   Subscribes to the `delay_alerts` and `surge_alerts` topics.
    *   When a message is received, it formats the alert and sends it to a configured notification channel (e.g., Slack, email, SMS).

## 6. Technology Stack

*   **Cloud Provider:** Confluent Cloud for managed Kafka and ksqlDB.
*   **Producers (Simulators):** Python or Go scripts using the `confluent-kafka` library.
*   **Stream Processing:** ksqlDB.
*   **Consumers:**
    *   **Dashboard Backend:** Python (Flask/FastAPI) with WebSockets.
    *   **Dashboard Frontend:** React/Vue with Leaflet/Mapbox.
    *   **Alerting Service:** Python.