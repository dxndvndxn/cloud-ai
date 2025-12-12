# database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import os
import asyncio
from contextlib import asynccontextmanager
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://ilyanazimov:@localhost:5432/ilyanazimov"
)

# Асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


# Dependency для получения сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Функция для проверки подключения к БД
async def test_connection() -> bool:
    """Проверяет подключение к базе данных"""
    try:
        async with AsyncSessionLocal() as session:
            # Простой запрос для проверки соединения
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            logger.info("✅ Подключение к базе данных успешно установлено")
            return value == 1
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к базе данных: {e}")
        return False


# Функция для получения информации о базе данных
async def get_database_info():
    """Получает информацию о базе данных"""
    try:
        async with AsyncSessionLocal() as session:
            # Получаем версию PostgreSQL
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()

            # Получаем имя текущей базы данных
            result = await session.execute(text("SELECT current_database()"))
            db_name = result.scalar()

            # Получаем имя пользователя
            result = await session.execute(text("SELECT current_user"))
            username = result.scalar()

            logger.info(f"📊 Информация о БД:")
            logger.info(f"   Версия: {version.split(',')[0]}")
            logger.info(f"   База данных: {db_name}")
            logger.info(f"   Пользователь: {username}")

            return {
                "version": version,
                "database": db_name,
                "username": username
            }
    except Exception as e:
        logger.error(f"❌ Ошибка при получении информации о БД: {e}")
        return None


# Функция для проверки существования таблиц
async def check_tables():
    """Проверяет существование таблиц в базе данных"""
    try:
        async with AsyncSessionLocal() as session:
            # Запрос для получения списка таблиц
            query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            result = await session.execute(query)
            tables = [row[0] for row in result.fetchall()]

            logger.info(f"📋 Найдено таблиц: {len(tables)}")
            if tables:
                logger.info("   Список таблиц:")
                for table in tables:
                    logger.info(f"   - {table}")

            return tables
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке таблиц: {e}")
        return []


# Функция для инициализации базы данных (создание таблиц)
async def init_db():
    """Создает все таблицы в базе данных"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Таблицы успешно созданы")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка при создании таблиц: {e}")
        return False


# Функция для комплексной проверки
async def run_database_checks():
    """Запускает все проверки базы данных"""
    logger.info("🔍 Запуск проверки подключения к базе данных...")

    # Проверка подключения
    connection_ok = await test_connection()
    if not connection_ok:
        logger.error("❌ Проверка подключения не пройдена")
        return False

    # Получение информации о БД
    info = await get_database_info()
    if not info:
        logger.error("❌ Не удалось получить информацию о БД")
        return False

    # Проверка таблиц
    tables = await check_tables()

    logger.info("✅ Все проверки завершены успешно")
    return True


# Асинхронный контекстный менеджер для сессий
@asynccontextmanager
async def get_db_session():
    """Контекстный менеджер для работы с сессией БД"""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# Функция для тестирования из командной строки
async def main():
    """Основная функция для тестирования из командной строки"""
    print("=" * 50)
    print("Тестирование подключения к базе данных")
    print("=" * 50)

    success = await run_database_checks()

    if success:
        print("\n✅ Все проверки пройдены успешно!")
        return 0
    else:
        print("\n❌ Обнаружены проблемы с подключением к БД")
        return 1


if __name__ == "__main__":
    # Запуск тестирования
    exit_code = asyncio.run(main())
    exit(exit_code)