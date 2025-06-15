from redis.asyncio import Redis
from pydantic import BaseModel
from typing import Optional

import uuid

class URLData(BaseModel):
    """
    Internal Pydantic model for storing URL data in Redis.
    It includes the 'url' itself and an optional 'name' field.
    """
    url: str
    name: Optional[str] = None # 'name' can be optional

class Domain:
    """
    Handles data operations with Redis, specifically for URL key-value pairs.
    Serializes Pydantic models to JSON before storing and deserializes them
    when retrieving.
    """
    def __init__(self, redis: Redis):
        self.redis = redis

    async def insert(self, key: str, url_data: URLData) -> None:
        """
        Inserts a URLData object into Redis under the given key.
        The URLData object is first serialized to a JSON string.
        """
        # Serialize the Pydantic model to a JSON string
        await self.redis.set(key, url_data.model_dump_json())

    async def get(self, key: str) -> Optional[URLData]:
        """
        Retrieves URL data from Redis for the given key.
        The retrieved JSON string is deserialized back into a URLData object.
        Returns None if the key does not exist.
        """
        redis_value = await self.redis.get(key)
        if redis_value:
            # Decode bytes to string and then parse JSON into URLData model
            return URLData.model_validate_json(redis_value)
        return None
    
    def generate_key(self) -> str:
        """
        Generates a unique key for storing URL data in Redis.
        """
        return uuid.uuid4().hex
