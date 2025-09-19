from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
import uuid
from app.models.queue_model import UserLogin,ChangePasswordRequest, Token, UserDetails, UserCreate
from app.utils.auth_utils import hash_password, verify_password, create_access_token, verify_token, generate_api_key
from app.db.auth_db import db
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*30

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Login endpoint that authenticates user and returns JWT token
    """
    # Get user from database
    user_record = await db.get_user_by_username(user_credentials.username, user_credentials.domain)
    
    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user_record['password'], user_record['salt']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is enabled
    if not user_record['user_enabled']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_record['user_uuid'])},
        expires_delta=access_token_expires
    )
    
    # Update last login
    await db.update_user_last_login(user_record['user_uuid'])
    
    # Convert user record to User model
    user = UserDetails(
        username=user_record['username'],
        user_email=user_record['user_email'],
        user_status=user_record['user_status'],
        user_type=user_record['user_type'],
        user_enabled=user_record['user_enabled'],
        extension=user_record['extension'],
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=user
    )

@router.get("/user-details", response_model=UserDetails)
async def get_current_user(user_uuid: str = Depends(verify_token)):
    """
    Get current user information
    """
    user_record = await db.get_user_by_uuid(uuid.UUID(user_uuid))
    
    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserDetails(
        username=user_record['username'],
        user_email=user_record['user_email'],
        user_status=user_record['user_status'],
        user_type=user_record['user_type'],
        user_enabled=user_record['user_enabled'],
        extension=user_record['extension']
    )

@router.post("/logout")
async def logout(user_uuid: str = Depends(verify_token)):
    """
    Logout endpoint (token invalidation would be handled client-side or with a token blacklist)
    """
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(user_uuid: str = Depends(verify_token)):
    """
    Refresh access token
    """
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_uuid},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    user_uuid: str = Depends(verify_token)
):
    """
    Change password for the current user
    """
    user_record = await db.get_user_by_uuid(uuid.UUID(user_uuid))
    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify current password
    if not verify_password(payload.current_password, user_record['password'], user_record['salt']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Hash new password
    new_password_hash, new_salt = hash_password(payload.new_password)

    # Update password in DB
    await db.change_user_password(user_record['user_uuid'], new_password_hash, new_salt)

    return {"message": "Password changed successfully"}