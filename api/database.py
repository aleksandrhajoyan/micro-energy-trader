import os
import asyncpg
import logging
import json

logger = logging.getLogger(__name__)

# Global connection pool
pool: asyncpg.Pool | None = None

def get_db_url() -> str:
    """
    Retrieve database URL from environment and clean it for asyncpg.
    Docker-compose provides 'postgresql+asyncpg://', but the raw asyncpg 
    driver prefers 'postgresql://'.
    """
    url = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@timescaledb:5432/energy_db"
    )
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    return url

async def connect_db():
    """Create a connection pool to the PostgreSQL/TimescaleDB database."""
    global pool
    url = get_db_url()
    try:
        pool = await asyncpg.create_pool(dsn=url, min_size=1, max_size=10)
        logger.info("Database connection pool created successfully.")
        await init_db()
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise e

async def close_db():
    """Close the database connection pool."""
    global pool
    if pool:
        await pool.close()
        logger.info("Database connection pool closed.")

async def init_db():
    global pool
    # Мы больше не создаем здесь пул заново, а используем уже готовый из connect_db()
    async with pool.acquire() as conn:
        # Создаем расширение TimescaleDB
        await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")

        # Таблица погодных метрик (ПРАВИЛЬНАЯ СТРУКТУРА)
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_metrics (
                time TIMESTAMPTZ NOT NULL,
                temperature DOUBLE PRECISION,
                wind_speed DOUBLE PRECISION,
                cloud_cover DOUBLE PRECISION,
                solar_irradiance DOUBLE PRECISION
            );
        """
        )

        try:
            await conn.execute(
                "SELECT create_hypertable('weather_metrics', 'time', if_not_exists => TRUE);"
            )
            logger.info("TimescaleDB hypertable 'weather_metrics' initialized.")
        except Exception as e:
            logger.warning(f"Hypertable notice: {e}")

        # Таблица сохраненных решений (ПРАВИЛЬНАЯ СТРУКТУРА)
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trading_decisions (
                id SERIAL PRIMARY KEY,
                thread_id TEXT UNIQUE NOT NULL,
                action TEXT NOT NULL,
                decision_data JSONB NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """
        )
        logger.info("Table 'trading_decisions' initialized.")

async def save_weather_data(data: dict):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO weather_metrics (time, temperature, wind_speed, cloud_cover, solar_irradiance)
            VALUES (NOW(), $1, $2, $3, $4);
        """,
            data["temperature"],
            data["wind_speed"],
            data["cloud_cover"],
            data["solar_irradiance"],
        )

async def save_trading_decision(thread_id: str, action: str, decision_data: dict):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO trading_decisions (thread_id, action, decision_data)
            VALUES ($1, $2, $3)
            ON CONFLICT (thread_id) DO UPDATE SET action = EXCLUDED.action, decision_data = EXCLUDED.decision_data;
        """,
            thread_id,
            action,
            json.dumps(decision_data),
        )