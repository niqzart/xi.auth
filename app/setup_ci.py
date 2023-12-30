import asyncio

from app.main import Base, engine  # type: ignore[attr-defined]


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_database())
