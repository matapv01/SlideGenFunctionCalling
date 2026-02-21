# File: backend/api/v1/authentication_router.py

from fastapi import APIRouter, Depends, HTTPException
from backend.api.schemas.auth_schema import (
    UserCreate, 
    UserLogin, 
    Token, 
    UserResponse, 
    ChangePasswordRequest  # Import thêm cái này
)
from backend.api.dependencies import get_auth_service, get_current_active_user
from backend.application.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.register_user(user_data.email, user_data.username, user_data.password)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")
    
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_active_user)):
    return current_user


@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}


@router.put("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    current_password = password_data.current_password
    new_password = password_data.new_password

    user_dict = auth_service.user_repo.get_by_id(current_user.id)
    
    auth_service.change_password(
        user_id=current_user.id,
        current_password=current_password,
        new_password=new_password,
        user_hashed_password=user_dict["hashed_password"]
    )
    
    return {"message": "Password changed successfully"}
