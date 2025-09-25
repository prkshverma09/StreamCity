# StreamCity: A Real-Time Digital Twin 🏙️

StreamCity is a real-time data streaming application that simulates and visualizes a city's public transport system. It provides a live map of vehicle locations, detects operational anomalies like delays and passenger surges, and reports vehicle breakdowns. This system is designed to provide a "digital twin" of the city's transit network, offering real-time insights for operators and passengers.

## Project Structure

-   `spec.md`: The detailed design specification for the project.
-   `plan.md`: The implementation plan and task breakdown.
-   `producers/`: Contains Python scripts that simulate data (vehicles, riders, etc.) and send it to Kafka.
-   `docker-compose.yml`: A Docker Compose file to easily set up a local Kafka environment for development.

## Getting Started

There are two primary ways to run this project: with a local Kafka stack via Docker, or by connecting to a managed Confluent Cloud instance.

### Option 1: Local Development with Docker (Recommended)

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
-   Using **ksqlDB** to process and analyze these real-time data streams.
-   Building a **frontend dashboard** to visualize the vehicle locations on a map.
-   Creating an **alerting service** for anomalies.