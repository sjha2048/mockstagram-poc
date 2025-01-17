import os
import time
import asyncio
import aiohttp
import redis
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
WORKER_ID = os.getenv('WORKER_ID')
REDIS_URL = os.getenv('REDIS_URL')
MOCKSTAGRAM_URL = os.getenv('MOCKSTAGRAM_URL')
MIN_ID = 1000000
MAX_ID = 1001000  # Reduced range for testing
BATCH_SIZE = 50

class Worker:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL)
        self.session = None

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        if self.session:
            await self.session.close()

    async def fetch_follower_count(self, influencer_id):
        try:
            url = f"{MOCKSTAGRAM_URL}/api/v1/influencers/{influencer_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['followerCount']
        except Exception as e:
            logger.error(f"Error fetching data for {influencer_id}: {e}")
        return None

    def get_my_influencers(self):
        worker_count = int(self.redis.get('worker_count') or 1)
        worker_id = int(WORKER_ID) - 1
        
        influencers = []
        for id in range(MIN_ID, MAX_ID):
            if (id - MIN_ID) % worker_count == worker_id:
                influencers.append(id)
        return influencers

    async def process_batch(self, influencer_ids):
        tasks = [self.fetch_follower_count(id) for id in influencer_ids]
        results = await asyncio.gather(*tasks)
        
        timestamp = datetime.utcnow().isoformat()
        
        for influencer_id, count in zip(influencer_ids, results):
            if count is not None:
                data = {
                    'influencer_id': str(influencer_id),
                    'follower_count': str(count),
                    'timestamp': timestamp
                }
                self.redis.xadd('follower_counts', data)

    async def run(self):
        await self.initialize()
        
        while True:
            start_time = time.time()
            
            # Register worker
            self.redis.setex(f'worker_{WORKER_ID}', 70, 'alive')
            worker_count = len(self.redis.keys('worker_*'))
            self.redis.set('worker_count', worker_count)
            
            my_influencers = self.get_my_influencers()
            
            # Process in batches
            for i in range(0, len(my_influencers), BATCH_SIZE):
                batch = my_influencers[i:i + BATCH_SIZE]
                await self.process_batch(batch)
            
            # Wait until next minute
            elapsed = time.time() - start_time
            if elapsed < 60:
                await asyncio.sleep(60 - elapsed)

async def main():
    worker = Worker()
    try:
        await worker.run()
    except Exception as e:
        logger.error(f"Worker error: {e}")
    finally:
        await worker.cleanup()

if __name__ == "__main__":
    asyncio.run(main())