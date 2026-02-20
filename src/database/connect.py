from contextlib import asynccontextmanager

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config import prj_configs
from src.database.models import Base
import asyncio


class DataBase:

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(DataBase, cls).__new__(cls)
        return cls.instance

    def __init__(self, echo=False):
        if hasattr(self, "_initialized"):
            return
        self.connect = prj_configs.connect_url
        self.async_engine = create_async_engine(
            self.connect,
            echo=echo,
            pool_pre_ping=True
        )
        self.session_maker = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            # , expire_on_commit=False,   чтобы не ловить MissingGreenlet
        )
        self._initialized = True


    def get_engine(self):
        return self.async_engine


    def get_session_maker(self):
        return self.session_maker

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        """
        автоматический rollback при ошибке
        гарантированный close
        """
        async with self.session_maker() as session:
            try:
                yield session
            except:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def dispose(self):
        # Закрывает все активные соединения
        await self.async_engine.dispose()


    async def check_connection(self) -> bool:
        try:
            async with self.async_engine.connect() as conn:
                res = await conn.execute(text("SELECT 1"))
                print('connect: Ok', res.scalars().fetchall())
            return True
        except SQLAlchemyError as e:
            print(f"DB connection error: {e}")
            return False

    async def get_table(self, table_name):
        async with self.session_maker() as session:
            result = await session.execute(select(table_name))
        return result.scalars().all()


    async def create_db(self):
        async with self.async_engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)

if __name__ == '__main__':


    db = DataBase()

    asyncio.run(db.check_connection())

    # Создание таблиц по models
    # Нужно создать саму базу вручную или через docker-compose.yaml
    #asyncio.run(db.create_db())