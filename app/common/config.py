from os import getenv
from pathlib import Path
from sys import modules

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy import MetaData, NullPool
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.common.cryptography import CryptographyProvider
from app.common.rabbit import RabbitDirectProducer
from app.common.sqla import MappingBase

current_directory: Path = Path.cwd()

load_dotenv(current_directory / ".env")

AVATARS_PATH: Path = current_directory / "avatars"

PRODUCTION_MODE: bool = getenv("PRODUCTION", "0") == "1"
TESTING_MODE: bool = "pytest" in modules

COOKIE_DOMAIN: str = getenv("COOKIE_DOMAIN", "localhost")
DATABASE_MIGRATED: bool = getenv("DATABASE_MIGRATED", "0") == "1"

DB_URL: str = getenv("DB_LINK", "postgresql+asyncpg://test:test@localhost:5432/test")
DB_SCHEMA: str | None = getenv("DB_SCHEMA", None)

MQ_URL: str = getenv("MQ_URL", "amqp://guest:guest@localhost/")
MQ_POCHTA_QUEUE: str = getenv("MQ_POCHTA_QUEUE", "pochta.send")

CRYPTOGRAPHY_KEYS: list[str] = getenv(
    "RESET_KEY", Fernet.generate_key().decode("utf-8")
).split("|")

DEMO_WEBHOOK_URL: str | None = getenv("DEMO_WEBHOOK_URL", None)
VACANCY_WEBHOOK_URL: str | None = getenv("VACANCY_WEBHOOK_URL", None)

MUB_KEY: str = getenv("MUB_KEY", "local")

SUPBOT_TOKEN: str | None = getenv("SUPBOT_TOKEN")
SUPBOT_GROUP_ID: str | None = getenv("SUPBOT_GROUP_ID")
SUPBOT_CHANNEL_ID: str | None = getenv("SUPBOT_CHANNEL_ID")
SUPBOT_POLLING: bool = getenv("SUPBOT_POLLING", "0") == "1"
SUPBOT_WEBHOOK_URL: str = getenv("SUPBOT_WEBHOOK_URL", "http://localhost:5100")

convention = {
    "ix": "ix_%(column_0_label)s",  # noqa: WPS323
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # noqa: WPS323
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # noqa: WPS323
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # noqa: WPS323
    "pk": "pk_%(table_name)s",  # noqa: WPS323
}

engine = create_async_engine(
    DB_URL,
    pool_recycle=280,  # noqa: WPS432
    echo=not PRODUCTION_MODE,
    poolclass=None if PRODUCTION_MODE else NullPool,
)
db_meta = MetaData(naming_convention=convention, schema=DB_SCHEMA)
sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase, MappingBase):
    __tablename__: str
    __abstract__: bool

    metadata = db_meta


pochta_producer = RabbitDirectProducer(queue_name=MQ_POCHTA_QUEUE)
cryptography_provider = CryptographyProvider(CRYPTOGRAPHY_KEYS)
