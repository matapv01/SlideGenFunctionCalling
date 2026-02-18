# File: backend/application/services/auth_service.py

import os
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import HTTPException, status
from backend.domain.ports.user_repository import UserRepository
from backend.domain.entities.user import User


class AuthService:
    """Xử lý toàn bộ business logic liên quan đến Authentication"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def get_password_hash(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_access_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            email: str = payload.get("sub")
            if email is None:
                raise JWTError()
            return email
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Không thể xác thực thông tin đăng nhập"
            )

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_email(email)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def register_user(self, email: str, username: str, password: str) -> User:
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email đã được đăng ký")
            
        hashed_password = self.get_password_hash(password)
        user_id = self.user_repo.create(email, username, hashed_password)
        
        # Fetch lại để trả về data đầy đủ
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=500, detail="Không thể tạo người dùng")
        return user

    def change_password(self, user_id: int, current_password: str, new_password: str, user_hashed_password: str) -> None:
        if not self.verify_password(current_password, user_hashed_password):
            raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng")
            
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Mật khẩu mới phải có ít nhất 6 ký tự")
            
        new_hashed = self.get_password_hash(new_password)
        self.user_repo.update_password(user_id, new_hashed)