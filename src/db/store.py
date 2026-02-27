"""
Database module using SQLite with SQLAlchemy.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from sqlalchemy import String, Integer, Boolean, DateTime, Text
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
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(Integer, nullable=False)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resource_usage: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Proxy(Base):
    __tablename__ = "proxies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    proxy_type: Mapped[str] = mapped_column(String(20), default="http")
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Fingerprint(Base):
    __tablename__ = "fingerprints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    platform: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    webgl_vendor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    webgl_renderer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    canvas_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    audio_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    fonts: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    user: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="success")
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    request_method: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    request_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    response_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Database:
    def __init__(self, db_path: str = "data/bower.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{self.db_path}",
            echo=False,
        )
        self.session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

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

    async def update_profile(
        self, profile_id: int, update_data: dict
    ) -> Optional[Profile]:
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

    async def create_proxy(self, proxy_data: dict) -> Proxy:
        async with self.session_maker() as session:
            proxy = Proxy(**proxy_data)
            session.add(proxy)
            await session.commit()
            await session.refresh(proxy)
            return proxy

    async def get_proxy(self, proxy_id: int) -> Optional[Proxy]:
        async with self.session_maker() as session:
            return await session.get(Proxy, proxy_id)

    async def list_proxies(self) -> List[Proxy]:
        async with self.session_maker() as session:
            from sqlalchemy import select

            result = await session.execute(select(Proxy))
            return list(result.scalars().all())

    async def update_proxy(self, proxy_id: int, update_data: dict) -> Optional[Proxy]:
        async with self.session_maker() as session:
            proxy = await session.get(Proxy, proxy_id)
            if proxy:
                for key, value in update_data.items():
                    setattr(proxy, key, value)
                proxy.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(proxy)
            return proxy

    async def delete_proxy(self, proxy_id: int) -> bool:
        async with self.session_maker() as session:
            proxy = await session.get(Proxy, proxy_id)
            if proxy:
                await session.delete(proxy)
                await session.commit()
                return True
            return False

    async def create_fingerprint(self, fingerprint_data: dict) -> Fingerprint:
        async with self.session_maker() as session:
            fingerprint = Fingerprint(**fingerprint_data)
            session.add(fingerprint)
            await session.commit()
            await session.refresh(fingerprint)
            return fingerprint

    async def get_fingerprint(self, fingerprint_id: int) -> Optional[Fingerprint]:
        async with self.session_maker() as session:
            return await session.get(Fingerprint, fingerprint_id)

    async def get_fingerprint_by_profile(
        self, profile_id: int
    ) -> Optional[Fingerprint]:
        async with self.session_maker() as session:
            from sqlalchemy import select

            result = await session.execute(
                select(Fingerprint).where(Fingerprint.profile_id == profile_id)
            )
            return result.scalar_one_or_none()

    async def list_fingerprints(self) -> List[Fingerprint]:
        async with self.session_maker() as session:
            from sqlalchemy import select

            result = await session.execute(select(Fingerprint))
            return list(result.scalars().all())

    async def update_fingerprint(
        self, fingerprint_id: int, update_data: dict
    ) -> Optional[Fingerprint]:
        async with self.session_maker() as session:
            fingerprint = await session.get(Fingerprint, fingerprint_id)
            if fingerprint:
                for key, value in update_data.items():
                    setattr(fingerprint, key, value)
                fingerprint.updated_at = datetime.utcnow()
                await session.commit()
                await session.refresh(fingerprint)
            return fingerprint

    async def delete_fingerprint(self, fingerprint_id: int) -> bool:
        async with self.session_maker() as session:
            fingerprint = await session.get(Fingerprint, fingerprint_id)
            if fingerprint:
                await session.delete(fingerprint)
                await session.commit()
                return True
            return False

    async def create_audit_log(self, log_data: dict) -> AuditLog:
        async with self.session_maker() as session:
            log_entry = AuditLog(**log_data)
            session.add(log_entry)
            await session.commit()
            await session.refresh(log_entry)
            return log_entry

    async def get_audit_log(self, log_id: int) -> Optional[AuditLog]:
        async with self.session_maker() as session:
            return await session.get(AuditLog, log_id)

    async def list_audit_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[str] = None,
        user: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[AuditLog]:
        async with self.session_maker() as session:
            from sqlalchemy import select, and_

            query = select(AuditLog).order_by(AuditLog.timestamp.desc())

            filters = []
            if event_type:
                filters.append(AuditLog.event_type == event_type)
            if user:
                filters.append(AuditLog.user == user)
            if start_date:
                filters.append(AuditLog.timestamp >= start_date)
            if end_date:
                filters.append(AuditLog.timestamp <= end_date)

            if filters:
                query = query.where(and_(*filters))

            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    async def count_audit_logs(
        self,
        event_type: Optional[str] = None,
        user: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        async with self.session_maker() as session:
            from sqlalchemy import select, func, and_

            query = select(func.count(AuditLog.id))

            filters = []
            if event_type:
                filters.append(AuditLog.event_type == event_type)
            if user:
                filters.append(AuditLog.user == user)
            if start_date:
                filters.append(AuditLog.timestamp >= start_date)
            if end_date:
                filters.append(AuditLog.timestamp <= end_date)

            if filters:
                query = query.where(and_(*filters))

            result = await session.execute(query)
            return result.scalar() or 0

    async def get_audit_logs_by_resource(
        self, resource_type: str, resource_id: str, limit: int = 50
    ) -> List[AuditLog]:
        async with self.session_maker() as session:
            from sqlalchemy import select, and_

            query = (
                select(AuditLog)
                .where(
                    and_(
                        AuditLog.resource_type == resource_type,
                        AuditLog.resource_id == resource_id,
                    )
                )
                .order_by(AuditLog.timestamp.desc())
                .limit(limit)
            )
            result = await session.execute(query)
            return list(result.scalars().all())

    async def close(self):
        await self.engine.dispose()
