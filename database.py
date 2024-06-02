from sqlalchemy import Column, Integer, Float, String, CheckConstraint, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker

async_engine = create_async_engine("sqlite+aiosqlite:///rolls.db")
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine("sqlite:///rolls.db")
sync_session = sessionmaker(sync_engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class RollOrm(Model):
    __tablename__ = "rolls"

    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    added_date = Column(String)
    removed_date = Column(String, nullable=True)

    __table_args__ = (
        CheckConstraint("CAST(length AS REAL) > 0"),
        CheckConstraint("CAST(weight AS REAL) > 0")
    )


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
