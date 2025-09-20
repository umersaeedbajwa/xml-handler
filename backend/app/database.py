import os
import asyncpg

from dotenv import load_dotenv
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Create database connection pool"""
        print(f"Connecting to database... {DATABASE_URL}")
        self.pool = await asyncpg.create_pool(DATABASE_URL)
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def fetch_all(self, query: str, *args):
        """Fetch all rows from query"""
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetch_one(self, query: str, *args):
        """Fetch one row from query"""
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def execute(self, query: str, *args):
        """Execute a query (INSERT, UPDATE, DELETE)"""
        async with self.pool.acquire() as connection:
            result = await connection.execute(query, *args)
            # Extract the number of affected rows from result string like "INSERT 0 1"
            return int(result.split()[-1]) if result else 0
   
# Global database instance
baseDB = Database()