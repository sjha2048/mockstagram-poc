# Mockstagram Database Queries Documentation

### 1. Raw Data Insertion
```sql
INSERT INTO follower_counts (influencer_id, follower_count, timestamp)
VALUES ($1, $2, $3)
```
**Purpose**: Stores raw follower count data points with one-minute resolution.

### 2. Running Average Update
```sql
INSERT INTO influencer_stats 
(influencer_id, current_count, average_count, count_samples, last_updated)
VALUES 
    ($1, $2::INTEGER, $2::DOUBLE PRECISION, 1, $3)
ON CONFLICT (influencer_id) DO UPDATE
SET 
    current_count = EXCLUDED.current_count,
    average_count = (
        (influencer_stats.average_count * influencer_stats.count_samples + 
        EXCLUDED.current_count::DOUBLE PRECISION) / 
        (influencer_stats.count_samples + 1)
    ),
    count_samples = influencer_stats.count_samples + 1,
    last_updated = EXCLUDED.last_updated
```
**Purpose**: Updates running statistics for each influencer, including incremental average computation.

### 3. Fetch Current Stats
```sql
SELECT current_count, average_count
FROM influencer_stats
WHERE influencer_id = $1
```
**Purpose**: Retrieves current statistics for an influencer.

### 4. Timeline Query
```sql
SELECT timestamp, follower_count
FROM follower_counts
WHERE influencer_id = $1
AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
```
**Purpose**: Retrieves historical data points for time-series visualization.
