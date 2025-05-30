import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiosqlite

from models import Base

# Путь к базе данных из переменных окружения
DATABASE_PATH = os.getenv("DATABASE_PATH", "youtube_data.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

# Создание асинхронного движка
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False}
)

# Создание фабрики сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Инициализация базы данных"""
    try:
        async with engine.begin() as conn:
            # Создание всех таблиц
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы базы данных созданы")
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        raise

async def close_db():
    """Закрытие соединения с базой данных"""
    await engine.dispose()

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии базы данных"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Вспомогательные функции для работы с базой данных
class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    @staticmethod
    async def get_or_create(session: AsyncSession, model, defaults=None, **kwargs):
        """Получить объект или создать новый"""
        from sqlalchemy import select
        
        stmt = select(model).filter_by(**kwargs)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()
        
        if instance:
            return instance, False
        else:
            params = dict(kwargs)
            if defaults:
                params.update(defaults)
            instance = model(**params)
            session.add(instance)
            await session.flush()
            return instance, True
    
    @staticmethod
    async def bulk_create(session: AsyncSession, model, objects):
        """Массовое создание объектов"""
        instances = [model(**obj) for obj in objects]
        session.add_all(instances)
        await session.flush()
        return instances
    
    @staticmethod
    async def paginate(session: AsyncSession, query, page: int = 1, per_page: int = 20):
        """Пагинация результатов"""
        from sqlalchemy import func, select
        
        # Подсчет общего количества
        count_stmt = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # Получение страницы результатов
        offset = (page - 1) * per_page
        paginated_query = query.limit(per_page).offset(offset)
        result = await session.execute(paginated_query)
        items = result.scalars().all()
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }

# Синхронные функции для Celery (так как Celery не поддерживает async)
def get_sync_engine():
    """Создание синхронного движка для Celery"""
    sync_db_url = f"sqlite:///{DATABASE_PATH}"
    return create_engine(
        sync_db_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )

sync_engine = get_sync_engine()
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

def get_sync_session() -> Session:
    """Получение синхронной сессии для Celery"""
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()