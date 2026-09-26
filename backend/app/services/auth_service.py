from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import hashlib
import secrets

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserCreate, UserLogin
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, create_refresh_token, decode_token


def _hash_token(token: str) -> str:
    """Hash a token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def _generate_token_family() -> str:
    """Generate a unique token family identifier."""
    return secrets.token_urlsafe(16)


# ==========================================
# Register User
# ==========================================
def register_user(db: Session, user_data: UserCreate):

    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise ValueError("Email already registered")

    hashed_password = hash_password(user_data.password)

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ==========================================
# Login User
# ==========================================
def login_user(db: Session, user_data: UserLogin):

    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(
        user_data.password,
        user.password,
    ):
        raise ValueError("Invalid email or password")

    return _create_token_pair(db, user)


# ==========================================
# Create Token Pair (Access + Refresh)
# ==========================================
def _create_token_pair(db: Session, user: User):
    from app.config import settings
    
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Store refresh token hash
    refresh_token_hash = _hash_token(refresh_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=expires_at,
    )
    
    db.add(refresh_token_record)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


# ==========================================
# Refresh Access Token with Rotation
# ==========================================
def refresh_access_token(db: Session, refresh_token: str):
    from app.config import settings
    from datetime import timedelta
    
    refresh_token_hash = _hash_token(refresh_token)
    
    # Find the refresh token record
    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == refresh_token_hash)
        .first()
    )
    
    if not token_record:
        raise ValueError("Invalid refresh token")
    
    # Check if token is revoked
    if token_record.is_revoked:
        # Check for reuse detection - if already revoked and someone tries to use it again
        if token_record.replaced_by_token_hash:
            # Token was rotated, this is a reuse attempt - potential theft!
            # Revoke ALL tokens for this user
            _revoke_all_user_tokens(db, token_record.user_id)
            raise ValueError("Token reuse detected - all sessions revoked")
        raise ValueError("Token has been revoked")
    
    # Check expiry - handle both timezone-aware and naive datetimes
    expires_at = token_record.expires_at
    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        # If expires_at is naive, assume UTC
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        raise ValueError("Refresh token has expired")
    
    # Get user
    user = token_record.user
    if not user or user.is_deleted:
        raise ValueError("User not found or deleted")
    
    # Rotate: mark current token as revoked and create new token pair
    token_family = _generate_token_family()
    new_access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    })
    new_refresh_token = create_refresh_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
    })
    
    new_refresh_token_hash = _hash_token(new_refresh_token)
    new_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    
    # Create new refresh token record
    new_token_record = RefreshToken(
        user_id=user.id,
        token_hash=new_refresh_token_hash,
        replaced_by_token_hash=new_refresh_token_hash,  # This will be updated after creation
        expires_at=new_expires_at,
    )
    
    # Mark old token as revoked and link to new one
    token_record.is_revoked = True
    token_record.replaced_by_token_hash = new_refresh_token_hash
    
    db.add(new_token_record)
    db.commit()
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


def _revoke_all_user_tokens(db: Session, user_id: int):
    """Revoke all refresh tokens for a user (used on logout or theft detection)."""
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    ).update({
        RefreshToken.is_revoked: True,
    })
    db.commit()


# ==========================================
# Logout / Revoke Tokens
# ==========================================
def logout_user(db: Session, user_id: int):
    """Revoke all refresh tokens for a user on logout."""
    _revoke_all_user_tokens(db, user_id)
    return {"message": "Logged out successfully"}


# ==========================================
# Revoke Specific Refresh Token
# ==========================================
def revoke_refresh_token(db: Session, refresh_token: str):
    """Revoke a specific refresh token."""
    refresh_token_hash = _hash_token(refresh_token)
    
    token_record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == refresh_token_hash)
        .first()
    )
    
    if token_record:
        token_record.is_revoked = True
        db.commit()
    
    return {"message": "Token revoked"}