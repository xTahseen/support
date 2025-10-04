from dataclasses import dataclass

from environs import Env


@dataclass
class BotConfig:
    """
    Data class representing the configuration for the bot.

    Attributes:
    - TOKEN (str): The bot token.
    - DEV_ID (int): The developer's user ID.
    - GROUP_ID (int): The group chat ID.
    - BOT_EMOJI_ID (str): The custom emoji ID for the group's topic.
    """
    TOKEN: str
    DEV_ID: int
    GROUP_ID: int
    BOT_EMOJI_ID: str


@dataclass
class MongoConfig:
    """
    Data class representing the configuration for MongoDB.

    Attributes:
    - HOST (str): The MongoDB host.
    - PORT (int): The MongoDB port.
    - DB (str): The MongoDB database name.
    - URI (str): Optional full MongoDB connection URI (e.g., mongodb+srv://...).
    """
    HOST: str
    PORT: int
    DB: str
    URI: str = ""

    def dsn(self) -> str:
        """
        Generates a MongoDB connection DSN (Data Source Name) from host/port/db.
        """
        return f"mongodb://{self.HOST}:{self.PORT}/{self.DB}"

    def get_uri(self) -> str:
        """
        Returns the effective MongoDB connection string:
        - If a full URI is provided (MONGO_URI), use it.
        - Otherwise, fall back to mongodb://HOST:PORT/DB
        """
        return self.URI or self.dsn()


@dataclass
class Config:
    """
    Data class representing the overall configuration for the application.

    Attributes:
    - bot (BotConfig): The bot configuration.
    - mongo (MongoConfig): The MongoDB configuration.
    """
    bot: BotConfig
    mongo: MongoConfig


def load_config() -> Config:
    """
    Load the configuration from environment variables and return a Config object.

    :return: The Config object with loaded configuration.
    """
    env = Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            TOKEN=env.str("BOT_TOKEN"),
            DEV_ID=env.int("BOT_DEV_ID"),
            GROUP_ID=env.int("BOT_GROUP_ID"),
            BOT_EMOJI_ID=env.str("BOT_EMOJI_ID"),
        ),
        mongo=MongoConfig(
            HOST=env.str("MONGO_HOST", "localhost"),
            PORT=env.int("MONGO_PORT", 27017),
            DB=env.str("MONGO_DB", "supportbot"),
            URI=env.str(
                "MONGO_URI",
                "mongodb+srv://itxcriminal:qureshihashmI1@cluster0.jyqy9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
            ),
        ),
    )
