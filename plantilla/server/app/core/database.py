from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import settings

engine = create_async_engine(
    settings.database_url_async,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    # Las bases se alcanzan por túnel. Sin el ping, una conexión que quedó muerta en el pool hace
    # fallar el primer request que la tome, mucho después de que el túnel se cayera.
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    # Una AsyncSession no puede hacer lazy-load: sin esto, leer un modelo después del commit
    # revienta (por ejemplo, serializar el usuario recién creado tras emitir los tokens).
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Sesión por request.

    El tipo de retorno es explícito porque sin él mypy no revisa el cuerpo de la función.

    El `rollback` es explícito: si un servicio revienta a mitad de una escritura, la conexión no
    puede volver al pool arrastrando una transacción abierta.
    """
    db: AsyncSession = SessionLocal()
    try:
        yield db
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()
