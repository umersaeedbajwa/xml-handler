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
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        print(f"Connecting to database... {DATABASE_URL}")
        try:
            self.pool = await asyncpg.create_pool(DATABASE_URL)
            print("✅ Database connection pool created successfully")
        except Exception as e:
            print(f"❌ Failed to create database connection pool: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            print("✅ Database connection pool closed")
    
    async def fetch_all(self, query: str, *args):
        """Fetch all rows from query"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Make sure to call connect() first.")
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetch_one(self, query: str, *args):
        """Fetch one row from query"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Make sure to call connect() first.")
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def execute(self, query: str, *args):
        """Execute a query (INSERT, UPDATE, DELETE)"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Make sure to call connect() first.")
        async with self.pool.acquire() as connection:
            result = await connection.execute(query, *args)
            # Extract the number of affected rows from result string like "INSERT 0 1"
            return int(result.split()[-1]) if result else 0
   
# Global database instance
baseDB = Database()