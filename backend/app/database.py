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
   
# Global database instance
baseDB = Database()