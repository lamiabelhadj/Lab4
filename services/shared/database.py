import asyncpg
from contextlib import asynccontextmanager
from .config import DATABASE_URL

db_pool = None


async def init_db():
    """Initialize database connection pool"""
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    return db_pool


async def close_db():
    """Close database connection pool"""
    global db_pool
    if db_pool:
        await db_pool.close()


async def get_db_pool():
    """Get database connection pool"""
    global db_pool
    if db_pool is None:
        db_pool = await init_db()
    return db_pool


async def create_tables():
    """Create required database tables"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS loan_applications (
                id SERIAL PRIMARY KEY,
                application_id VARCHAR(255) UNIQUE NOT NULL,
                amount DECIMAL(12, 2) NOT NULL,
                duration INTEGER NOT NULL,
                income DECIMAL(12, 2) NOT NULL,
                id_document VARCHAR(255),
                salary_slip VARCHAR(255),
                contract_path VARCHAR(255),
                amortization_path VARCHAR(255),
                extracted_income DECIMAL(12, 2),
                status VARCHAR(50) DEFAULT 'Submitted',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
