from fastapi import FastAPI, HTTPException
import asyncpg
import os
from datetime import datetime, timedelta

app = FastAPI()
DB_URL = os.getenv('DB_URL')

async def get_db():
    return await asyncpg.connect(DB_URL)

@app.on_event("startup")
async def startup():
    app.state.db = await get_db()

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()

@app.get("/influencers/{influencer_id}")
async def get_influencer(influencer_id: int):
    stats = await app.state.db.fetchrow('''
        SELECT current_count, average_count, last_updated
        FROM influencer_stats
        WHERE influencer_id = $1
    ''', influencer_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Influencer not found")

    timeline = await app.state.db.fetch('''
        SELECT timestamp, follower_count
        FROM follower_counts
        WHERE influencer_id = $1
        AND timestamp > NOW() - INTERVAL '1 hour'
        ORDER BY timestamp DESC
    ''', influencer_id)

    return {
        "influencer_id": influencer_id,
        "current_count": stats['current_count'],
        "average_count": round(stats['average_count'], 2),
        "last_updated": stats['last_updated'],
        "timeline": [
            {
                "timestamp": t['timestamp'].isoformat(),
                "count": t['follower_count']
            }
            for t in timeline
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)