import json
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from .models import UserData


class RedisStorage:
    """MongoDB-backed storage for managing user data (class name preserved for compatibility)."""

    COLLECTION = "users"

    def __init__(self, mongo_db: AsyncIOMotorDatabase) -> None:
        """
        Initialize storage with a MongoDB database.
        :param mongo_db: AsyncIOMotorDatabase instance.
        """
        self.db = mongo_db
        self.col = self.db[self.COLLECTION]

    async def _get(self, filter_: dict) -> dict | None:
        """
        Retrieves a single document from MongoDB based on filter.
        """
        return await self.col.find_one(filter_)

    async def _set(self, filter_: dict, value: dict) -> None:
        """
        Upserts a document in MongoDB.
        """
        await self.col.update_one(filter_, {"$set": value}, upsert=True)

    async def get_by_message_thread_id(self, message_thread_id: int) -> UserData | None:
        """
        Retrieves user data based on message thread ID.
        """
        doc = await self._get({"message_thread_id": message_thread_id})
        if doc:
            doc.pop("_id", None)
        return UserData(**doc) if doc else None

    async def get_user(self, id_: int) -> UserData | None:
        """
        Retrieves user data based on user ID.
        """
        doc = await self._get({"id": id_})
        if doc:
            doc.pop("_id", None)
        return UserData(**doc) if doc else None

    async def update_user(self, id_: int, data: UserData) -> None:
        """
        Updates user data (upsert).
        """
        # Ensure we store a plain dict
        json_data = json.loads(json.dumps(data.to_dict()))
        await self._set({"id": id_}, json_data)

    async def get_all_users_ids(self) -> list[int]:
        """
        Retrieves all user IDs stored in the collection.
        """
        cursor = self.col.find({}, {"id": 1, "_id": 0})
        return [doc["id"] async for doc in cursor]
