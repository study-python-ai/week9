from fastapi import APIRouter, Depends, status

from app.api.v2.controllers.user_controller import UserController
from app.common.dependencies import get_current_user
from app.dependencies import get_user_model
from app.models.user_model import User, UserModel
from app.schemas.common import (
    ChangePasswordRequest,
    LoginUserRequest,
    RegisterUserRequest,
    Token,
    UpdateUserRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/v2/users", tags=["v2-users"])


def get_user_controller(
    user_model: UserModel = Depends(get_user_model),
) -> UserController:
    return UserController(user_model)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterUserRequest,
    controller: UserController = Depends(get_user_controller),
):
    """회원가입"""
    return controller.register(request)


@router.post("/login", response_model=Token)
def login(
    request: LoginUserRequest, controller: UserController = Depends(get_user_controller)
):
    """로그인"""
    return controller.login(request)


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """로그아웃"""
    return controller.logout(current_user)


@router.get("/{id}", response_model=UserResponse)
def get_profile(id: int, controller: UserController = Depends(get_user_controller)):
    """사용자 프로필 조회"""
    return controller.get_profile(id)


@router.patch("/{id}", response_model=UserResponse)
def update_profile(
    id: int,
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """사용자 정보 수정"""
    return controller.update_profile(id, request, current_user)


@router.patch("/{id}/password", status_code=status.HTTP_200_OK)
def change_password(
    id: int,
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """비밀번호 변경"""
    return controller.change_password(id, request, current_user)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    id: int,
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """회원 탈퇴"""
    controller.delete_account(id, current_user)
