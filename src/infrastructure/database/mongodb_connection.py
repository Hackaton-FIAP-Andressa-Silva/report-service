from motor.motor_asyncio import AsyncIOMotorClient
from src.infrastructure.config import settings

_client: AsyncIOMotorClient = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URL)
    return _client


def get_database():
    client = get_mongo_client()
    return client[settings.MONGODB_DATABASE]
