import os
import asyncio
import asyncpg
import redis
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROCESSOR_ID = os.getenv('PROCESSOR_ID')
REDIS_URL = os.getenv('REDIS_URL')
DB_URL = os.getenv('DB_URL')
BATCH_SIZE = 100

class Processor:
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL)
        self.db = None
        self.consumer_group = 'processors'
        self.stream_key = 'follower_counts'

    async def initialize(self):
        self.db = await asyncpg.connect(DB_URL)
        try:
            self.redis.xgroup_create(self.stream_key, self.consumer_group, mkstream=True)
        except redis.exceptions.ResponseError:
            pass

    async def update_stats(self, influencer_id, follower_count, timestamp):
        async with self.db.transaction():
            # Insert raw data
            await self.db.execute('''
                INSERT INTO follower_counts (influencer_id, follower_count, timestamp)
                VALUES ($1, $2, $3)
            ''', influencer_id, follower_count, timestamp)

            # Update running average
            await self.db.execute('''
                INSERT INTO influencer_stats 
                (influencer_id, current_count, average_count, count_samples, last_updated)
                VALUES ($1, $2, $2, 1, $3)
                ON CONFLICT (influencer_id) DO UPDATE
                SET 
                    current_count = $2,
                    average_count = (influencer_stats.average_count * influencer_stats.count_samples + $2::float) 
                                  / (influencer_stats.count_samples + 1),
                    count_samples = influencer_stats.count_samples + 1,
                    last_updated = $3
            ''', influencer_id, follower_count, timestamp)

    async def process_messages(self):
        while True:
            try:
                messages = self.redis.xreadgroup(
                    self.consumer_group,
                    f'processor-{PROCESSOR_ID}',
                    {self.stream_key: '>'},
                    count=BATCH_SIZE,
                    block=1000
                )

                if not messages:
                    await asyncio.sleep(0.1)
                    continue

                for _, entries in messages:
                    for message_id, data in entries:
                        try:
                            influencer_id = int(data[b'influencer_id'])
                            follower_count = int(data[b'follower_count'])
                            timestamp = datetime.fromisoformat(data[b'timestamp'].decode())
                            
                            await self.update_stats(influencer_id, follower_count, timestamp)
                            self.redis.xack(self.stream_key, self.consumer_group, message_id)
                            
                        except Exception as e:
                            logger.error(f"Error processing message {message_id}: {e}")

            except Exception as e:
                logger.error(f"Stream reading error: {e}")
                await asyncio.sleep(1)

    async def run(self):
        await self.initialize()
        await self.process_messages()

async def main():
    processor = Processor()
    try:
        await processor.run()
    except Exception as e:
        logger.error(f"Processor error: {e}")

if __name__ == "__main__":
    asyncio.run(main())