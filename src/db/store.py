"""
Database module using SQLite with SQLAlchemy.
"""
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

from sqlalchemy import String, Integer, Boolean, DateTime, Text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    use_case: Mapped[str] = mapped_column(String(100), nullable=True)
    browser_engine: Mapped[str] = mapped_column(String(50), default="chromium")
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    proxy: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    proxy_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    proxy_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resolution: Mapped[str] = mapped_column(String(20), default="1920x1080")
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    headless: Mapped[bool] = mapped_column(Boolean, default=True)
    advanced_settings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(Integer, nullable=False)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resource_usage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Database:
    def __init__(self, db_path: str = "data/bower.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{self.db_path}",
            echo=False,
        )
        self.session_maker = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized")

    async def create_profile(self, profile_data: dict) -> Profile:
        async with self.session_maker() as session:
            profile = Profile(**profile_data)
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
            return profile

    async def get_profile(self, profile_id: int) -> Optional[Profile]:
        async with self.session_maker() as session:
            return await session.get(Profile, profile_id)

    async def get_profile_by_name(self, name: str) -> Optional[Profile]:
        async with self.session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(Profile).where(Profile.name == name))
            return result.scalar_one_or_none()

    async def list_profiles(self) -> List[Profile]:
        async with self.session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(Profile))
            return list(result.scalars().all())

    async def update_profile(self, profile_id: int, update_data: dict) -> Optional[Profile]:
        async with self.session_maker() as session:
            profile = await session.get(Profile, profile_id)
            if profile:
                for key, value in update_data.items():
                    setattr(profile, key, value)
                profile.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(profile)
            return profile

    async def delete_profile(self, profile_id: int) -> bool:
        async with self.session_maker() as session:
            profile = await session.get(Profile, profile_id)
            if profile:
                await session.delete(profile)
                await session.commit()
                return True
            return False

    async def create_session_record(self, session_data: dict) -> Session:
        async with self.session_maker() as session:
            session_record = Session(**session_data)
            session.add(session_record)
            await session.commit()
            await session.refresh(session_record)
            return session_record

    async def close(self):
        await self.engine.dispose()
