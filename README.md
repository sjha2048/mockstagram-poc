
# Mockstagram

A distributed service poc for influencer follower count tracking.

## Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:sjha2048/mockstagram-poc.git
   cd mockstagram-poc
   ```

2. **Install Docker and Docker Compose:**
   - [Install Docker](https://docs.docker.com/get-docker/)
   - [Install Docker Compose](https://docs.docker.com/compose/install/)

3. **Start services using Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Access the API:**
   The API is available at `http://localhost:8000`.

## API Usage

### Get Influencer Stats
**Endpoint:**
```http
GET /influencers/{influencer_id}
```

**Response Example:**
```json
{
   "influencer_id": 1000000,
   "current_count": 256544,
   "average_count": 256544,
   "last_updated": "2025-01-16T17:32:12.357741+00:00",
   "timeline": [
    {
      "timestamp": "2025-01-16T17:32:12.357741+00:00",
      "count": 256544
    }
    ]
}
```
