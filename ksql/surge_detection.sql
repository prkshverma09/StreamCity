-- Step 1: Create a STREAM on the `rider_tapped_on` topic.
-- This defines the schema for incoming rider tap events.

CREATE STREAM rider_tapped_on_stream (
    `event_id` VARCHAR,
    `rider_id` VARCHAR,
    `station_id` VARCHAR,
    `latitude` DOUBLE,
    `longitude` DOUBLE,
    `timestamp` VARCHAR
) WITH (
    KAFKA_TOPIC = 'rider_tapped_on',
    VALUE_FORMAT = 'JSON',
    PARTITIONS = 1 -- Or match your topic partition count
);

-- Step 2: Create a new stream for surge alerts.
-- This query uses a 1-minute tumbling window to count rider taps in a specific geographic area.
-- GEOHASH is used to define the geographic zones. A precision of 5 covers an area of ~4.9km x 4.9km.
-- If the tap count in a zone exceeds 10 within a minute, a new event is emitted to the `surge_alerts` topic.

CREATE STREAM surge_alerts WITH (KAFKA_TOPIC='surge_alerts') AS
    SELECT
        GEOHASH(latitude, longitude, 5) AS geohash,
        COUNT(*) AS tap_count,
        WINDOWSTART as window_start,
        WINDOWEND as window_end
    FROM
        rider_tapped_on_stream
    WINDOW TUMBLING (SIZE 1 MINUTE)
    GROUP BY
        GEOHASH(latitude, longitude, 5)
    HAVING
        COUNT(*) > 10 -- Threshold for surge detection
    EMIT CHANGES;

-- To query the surge alerts stream (for testing in the ksqlDB editor):
-- SET 'auto.offset.reset' = 'earliest';
-- SELECT * FROM surge_alerts EMIT CHANGES;