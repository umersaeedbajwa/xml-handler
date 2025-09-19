import uuid
from datetime import datetime
from app.database import baseDB 

class AuthDB:
    def __init__(self):
        self.baseQuery = """
            SELECT u.user_uuid, u.domain_uuid, u.contact_uuid, u.username, u.password, u.salt,
                       u.user_email, u.user_status, u.user_type, u.user_enabled, e.extension
            FROM v_users u
            LEFT JOIN v_domains d ON u.domain_uuid = d.domain_uuid
            LEFT JOIN v_extension_users eu ON u.user_uuid = eu.user_uuid
            LEFT JOIN v_extensions e ON eu.extension_uuid = e.extension_uuid
        """

    async def get_user_by_username(self, username: str, domain: str = None):
        """Get user by username"""
        async with baseDB.pool.acquire() as connection:
            query = f"""
                {self.baseQuery}
                WHERE u.username = $1  AND (d.domain_name = $2 OR d.domain_name IS NULL)
                AND u.user_enabled = 'true'
            """
            return await connection.fetchrow(query, username, domain)

    async def get_user_by_uuid(self, user_uuid: uuid.UUID):
        """Get user by UUID"""
        async with baseDB.pool.acquire() as connection:
            query = f"""
                {self.baseQuery}
                WHERE u.user_uuid = $1 AND u.user_enabled = 'true'
            """
            return await connection.fetchrow(query, user_uuid)
    
    async def update_user_last_login(self, user_uuid: uuid.UUID):
        """Update user's last login timestamp"""
        async with baseDB.pool.acquire() as connection:
            query = """
                UPDATE v_users 
                SET update_date = $1 
                WHERE user_uuid = $2
            """
            await connection.execute(query, datetime.utcnow(), user_uuid)

    async def change_user_password(self, user_uuid: uuid.UUID, new_password: str, new_salt: str = None):
        """Change user's password (and optionally salt)"""
        async with baseDB.pool.acquire() as connection:
            if new_salt is not None:
                query = """
                    UPDATE v_users
                    SET password = $1, salt = $2, update_date = $3
                    WHERE user_uuid = $4
                """
                await connection.execute(query, new_password, new_salt, datetime.utcnow(), user_uuid)
            else:
                query = """
                    UPDATE v_users
                    SET password = $1, update_date = $2
                    WHERE user_uuid = $3
                """
                await connection.execute(query, new_password, datetime.utcnow(), user_uuid)
# Global database instance
db = AuthDB()