# Mockstagram POC - Design Overview

## Key Design Decisions

### 1. Influencer ID Distribution
implemented a simple round-robin distribution strategy for handling influencer IDs across multiple workers:

```python
worker_assigned_ids = [id for id in range(MIN_ID, MAX_ID) 
                      if (id - MIN_ID) % total_workers == worker_id]
```

For example, with 2 workers and IDs from 1000000 to 1001000:
- Worker 1 gets: 1000000, 1000002, 1000004...
- Worker 2 gets: 1000001, 1000003, 1000005...

This ensures:
- Even distribution of load
- No central coordinator needed
- Automatic rebalancing when workers are added/removed
- No shared state required

### 2. Running Average Computation
We use an incremental formula to compute running averages without storing all historical values:

```sql
new_average = (old_average * count + new_value) / (count + 1)
```

This is implemented in SQL as:
```sql
average_count = (influencer_stats.average_count * influencer_stats.count_samples + new_value) 
                / (influencer_stats.count_samples + 1)
```

Benefits:
- No need to scan historical data
- Single atomic database operation

### 3. Tech Stack used

#### Redis Streams 

Redis Streams is used as the queueing mechanism to distribute follower count data between workers and processors. Workers publish fetched data to a Redis stream, and processors consume it using consumer groups for further processing and storage.

#### TimescaleDB

TimescaleDB is used to store time-series data of influencer follower counts. It handles both the raw data points for historical tracking and the computed metrics like running averages, enabling efficient querying and aggregation.