# create_tables.py
import asyncio
from database import engine, Base
import models  # this import is important — it registers all models

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully!")

asyncio.run(create_tables())