CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS follower_counts (
    influencer_id INTEGER,
    follower_count INTEGER,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (influencer_id, timestamp)
);

SELECT create_hypertable('follower_counts', 'timestamp', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS influencer_stats (
    influencer_id INTEGER PRIMARY KEY,
    current_count INTEGER,
    average_count DOUBLE PRECISION,
    count_samples INTEGER,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_follower_counts_time 
ON follower_counts (influencer_id, timestamp DESC);