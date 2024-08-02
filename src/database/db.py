import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.conf.config import settings


class DataBaseSessionManager:
    def __init__(self, url: str):
        """
        The __init__ function is the constructor for a class. It is called when an object of that class
        is instantiated, and it sets up the attributes of that object. In this case, we are creating a
        database connection engine and session maker using SQLAlchemy's create_engine() function.

        :param self: Represent the instance of the class
        :param url: str: Create an engine
        :return: The class itself
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        The session function is a coroutine that returns an async context manager.
        The context manager yields a database session, and then closes the session
        when the block exits. The close method rolls back any uncommitted changes to
        the database.

        :param self: Represent the instance of the class
        :return: A context manager, which is a generator that can be used with the async with statement
        """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session

        except Exception as e:
            print(e)
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DataBaseSessionManager(settings.SQLALCHEMY_DATABASE_URL)


async def get_db():
    """
    The get_db function is a coroutine that returns an async context manager.
    When the context manager is entered, it yields a database session; when the
    context manager exits, it closes the session. The get_db function itself can be
    used as an async context manager:

    :return: A context manager that allows you to use async with
    """
    async with sessionmanager.session() as session:
        yield session

       
