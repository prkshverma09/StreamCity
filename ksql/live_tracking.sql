-- Step 1: Create a STREAM on the `vehicle_locations` topic.
-- This defines the schema for the incoming data and tells ksqlDB how to read it.

CREATE STREAM vehicle_locations_stream (
    `vehicle_id` VARCHAR,
    `type` VARCHAR,
    `latitude` DOUBLE,
    `longitude` DOUBLE,
    `passenger_count` INTEGER,
    `status` VARCHAR,
    `timestamp` VARCHAR
) WITH (
    KAFKA_TOPIC = 'vehicle_locations',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 1 -- Or match your topic partition count
);

-- Step 2: Create a materialized TABLE for live vehicle data.
-- This table will always store the most recent location and status for each vehicle_id.
-- It is continuously updated as new events arrive in the stream.

CREATE TABLE live_vehicle_table AS
    SELECT
        `vehicle_id` AS vehicle_id,
        LATEST_BY_OFFSET(`type`) AS type,
        LATEST_BY_OFFSET(`latitude`) AS latitude,
        LATEST_BY_OFFSET(`longitude`) AS longitude,
        LATEST_BY_OFFSET(`passenger_count`) AS passenger_count,
        LATEST_BY_OFFSET(`status`) AS status,
        LATEST_BY_OFFSET(`timestamp`) AS last_updated
    FROM
        vehicle_locations_stream
    GROUP BY
        `vehicle_id`
    EMIT CHANGES;

-- To query the live table (for testing in the ksqlDB editor):
-- SET 'auto.offset.reset' = 'earliest';
-- SELECT * FROM live_vehicle_table EMIT CHANGES;