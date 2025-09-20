from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

# Queue Models
class QueueCreate(BaseModel):
    queue_name: str
    extension: str
    strategy: str
    max_wait_time: int
    discard_abandoned: int
    context: str
    description: Optional[str] = None

class Queue(QueueCreate):
    id: int
    tenant_id: int

class QueueAgent(BaseModel):
    id: int
    queue_id: int
    agent_uuid: uuid.UUID

# Authentication Models
class UserLogin(BaseModel):
    username: str
    password: str
    domain: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    user_email: EmailStr
    user_type: str = "user"
    extension: Optional[str] = None
    domain: Optional[str] = None

class UserDetails(BaseModel):
    username: str
    user_email: str
    user_status: str
    user_type: str
    user_enabled: bool
    extension: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserDetails

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str