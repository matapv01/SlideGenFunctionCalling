from web.backend.app.models import UserCreate, UserLogin, Token, UserResponse, User
from datetime import timedelta
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status, Depends, Query, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from web.backend.app.models import TokenData, UserResponse
from web.backend.app.resource.database import get_user_by_email, get_db, create_user, get_user_by_id

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Bearer token scheme
security = HTTPBearer()
router = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return TokenData(email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate user with email and password"""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    token_data = decode_access_token(token)

    user = get_user_by_email(token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return UserResponse(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        created_at=user["created_at"],
        is_active=bool(user["is_active"])
    )


async def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Get current active user (check if user is not disabled)"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_user_from_token_param(token: str = Query(...)) -> UserResponse:
    """Get current user from token query parameter (for EventSource/SSE)"""
    token_data = decode_access_token(token)

    user = get_user_by_email(token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        created_at=user["created_at"],
        is_active=bool(user["is_active"])
    )

    if not user_response.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user_response


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user
    user_id = create_user(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )

    # Fetch created user
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")

    return UserResponse(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        created_at=user["created_at"],
        is_active=bool(user["is_active"])
    )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user and return JWT token"""
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token_expires = timedelta(minutes=60 * 24)  # 24 hours
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}


@router.put("/change-password")
async def change_password(
    password_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Change user password"""
    current_password = password_data.get('current_password')
    new_password = password_data.get('new_password')

    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Validate new password
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")

    # Update password in database
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            new_hashed_password = get_password_hash(new_password)
            cursor.execute(
                'UPDATE users SET hashed_password = ? WHERE id = ?',
                (new_hashed_password, current_user.id)
            )
            conn.commit()
            return {"message": "Password changed successfully"}
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")
