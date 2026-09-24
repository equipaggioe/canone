from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    # Las bases se alcanzan por túnel. Sin el ping, una conexión que
    # quedó muerta en el pool hace fallar el primer request que la tome,
    # mucho después de que el túnel se cayera.
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    # Una AsyncSession no puede hacer lazy-load: sin esto, leer un
    # modelo después del commit revienta (por ejemplo, serializar el
    # usuario recién creado tras emitir los tokens).
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Sesión por request.

    Sin `rollback` a mano: al salir del bloque, `close()` revierte lo
    que quedó sin commit, también si el servicio levantó una excepción,
    y la conexión vuelve limpia al pool.
    """
    async with SessionLocal() as db:
        yield db
