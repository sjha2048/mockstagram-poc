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

