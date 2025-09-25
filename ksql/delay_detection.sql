-- Step 1: Create a ksqlDB TABLE from the `vehicle_routes` topic.
-- This table will hold our static route data. We assume the `producer_routes.py`
-- script has been run once to populate this topic.
-- The primary key of the table is the route_id.

CREATE TABLE vehicle_routes_table (
    `route_id` VARCHAR PRIMARY KEY,
    `vehicle_id` VARCHAR,
    `vehicle_type` VARCHAR,
    `path` ARRAY<ARRAY<DOUBLE>>,
    `expected_travel_time_minutes` INTEGER
) WITH (
    KAFKA_TOPIC = 'vehicle_routes',
    VALUE_FORMAT = 'JSON'
);

-- Note: The following is a simplified approach to delay detection for this example.
-- A full implementation would require a UDF (User-Defined Function) to calculate
-- a vehicle's progress along a complex path and compare it to an expected schedule.

-- For this simulation, we'll define a "delay" as a vehicle that is "in_service"
-- but has not had a location update for a significant amount of time, suggesting
-- it is stuck or has an issue. We can achieve this by monitoring the time difference
-- between consecutive messages for the same vehicle.

-- Step 2: Create a stream that calculates the time between location updates.

CREATE STREAM vehicle_updates_with_time_diff AS
SELECT
    vehicle_id,
    LATEST_BY_OFFSET(status) as status,
    (ROWTIME - LAG(ROWTIME) OVER (PARTITION BY vehicle_id WITHIN 30 MINUTES)) / 1000 AS time_since_last_update_seconds
FROM
    vehicle_locations_stream
GROUP BY vehicle_id;

-- Step 3: Create the `delay_alerts` stream.
-- This stream will emit an alert if a vehicle is "in_service" and the time since
-- its last update exceeds a threshold (e.g., 120 seconds).

CREATE STREAM delay_alerts WITH (KAFKA_TOPIC='delay_alerts') AS
SELECT
    vehicle_id,
    'Vehicle may be delayed. No update for ' + CAST(time_since_last_update_seconds AS VARCHAR) + ' seconds.' AS alert_message,
    time_since_last_update_seconds
FROM
    vehicle_updates_with_time_diff
WHERE
    status = 'in_service' AND time_since_last_update_seconds > 120 -- 2-minute threshold
EMIT CHANGES;

-- To query the delay alerts stream (for testing in the ksqlDB editor):
-- SET 'auto.offset.reset' = 'earliest';
-- SELECT * FROM delay_alerts EMIT CHANGES;