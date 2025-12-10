#!/bin/bash
set -e

echo "Waiting for database to be ready..."
while ! python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def check_db():
    engine = create_async_engine(settings.DATABASE_URL)
    try:
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        return True
    except Exception as e:
        print(f'DB check failed: {e}')
        return False
    finally:
        await engine.dispose()

exit(0 if asyncio.run(check_db()) else 1)
" 2>&1; do
    echo "Database not ready, waiting..."
    sleep 2
done

echo "Database is ready!"

echo "Running database migrations..."
alembic upgrade head

echo "Seeding built-in tools..."
python -c "
import asyncio
from app.core.database import async_session_maker
from app.services.tool_service import ToolService

async def seed():
    async with async_session_maker() as session:
        service = ToolService(session)
        await service.seed_builtin_tools()

asyncio.run(seed())
"

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 58431
