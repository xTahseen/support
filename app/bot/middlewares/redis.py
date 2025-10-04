from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User, Chat
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.bot.utils.redis import RedisStorage
from app.bot.utils.redis.models import UserData
from app.bot.utils.texts import SUPPORTED_LANGUAGES


class RedisMiddleware(BaseMiddleware):
    """
    Middleware for integrating MongoDB-backed storage with Aiogram.
    (Class name kept as RedisMiddleware for compatibility with existing imports.)

    Args:
        mongo_db (AsyncIOMotorDatabase): The MongoDB database for data storage.
    """

    def __init__(self, mongo_db: AsyncIOMotorDatabase) -> None:
        """
        Initializes the storage middleware instance.

        :param mongo_db: The MongoDB database for data storage.
        """
        self.mongo_db = mongo_db

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Call the middleware.

        :param handler: The handler function.
        :param event: The Telegram event.
        :param data: Additional data.
        :return: The result of the handler function.
        """
        redis = RedisStorage(self.mongo_db)  # Mongo-backed storage (class name preserved)

        # Extract the chat and user objects from data
        chat: Chat = data.get("event_chat")
        user: User = data.get("event_from_user")

        # Check if the chat type is private and the user object is not None
        if chat.type == "private" and user is not None:
            # Retrieve user data based on user ID
            user_redis = await redis.get_user(user.id)
            user_data = user_redis or UserData(
                message_thread_id=None,
                message_silent_id=None,
                message_silent_mode=False,
                is_banned=False,
                id=user.id,
                full_name=user.full_name,
                username=f"@{user.username}" if user.username else "-",
            )
            if user_redis:
                user_data.full_name = user.full_name
                user_data.username = f"@{user.username}" if user.username else "-"

            if len(SUPPORTED_LANGUAGES.keys()) == 1:
                # If only one language is supported, set user language_code to the first language
                user_data.language_code = list(SUPPORTED_LANGUAGES.keys())[0]

            # Update user data
            await redis.update_user(user.id, user_data)
        else:
            # For group chats or if the user object is None, set user_data to None
            user_data = None

        # Add storage and user_data to data for use in subsequent handlers
        data["redis"] = redis  # key preserved for DI compatibility
        data["user_data"] = user_data

        # Call the handler function with the event and data
        return await handler(event, data)
