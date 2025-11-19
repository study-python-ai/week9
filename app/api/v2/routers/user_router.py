"""
사용자 관련 API 엔드포인트를 정의하는 라우터 모듈.

이 모듈은 사용자 인증, 프로필 관리, 비밀번호 변경, 회원 탈퇴 등의 기능을 제공합니다.
모든 엔드포인트는 /api/v2/users 경로 하위에 정의됩니다.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v2.controllers.user_controller import UserController
from app.core.db.dependencies import get_db, get_user_model
from app.core.security.dependencies import get_current_user
from app.models.user_model import User
from app.schemas import (
    ChangePasswordRequest,
    LoginUserRequest,
    RegisterUserRequest,
    Token,
    UpdateUserRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/v2/users", tags=["v2-users"])


def get_user_controller(db: Session = Depends(get_db)) -> UserController:
    """
    UserController 의존성 주입 함수.

    Args:
        db: 데이터베이스 세션

    Returns:
        UserController: 사용자 컨트롤러 인스턴스
    """
    return UserController(get_user_model(db))


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterUserRequest,
    controller: UserController = Depends(get_user_controller),
):
    """
    회원가입.

    새로운 사용자를 등록합니다.

    Args:
        request: 회원가입 요청 데이터
        controller: 사용자 컨트롤러

    Returns:
        UserResponse: 등록된 사용자 정보

    Raises:
        HTTPException: 이미 존재하는 이메일인 경우 400 에러
        HTTPException: 유효하지 않은 데이터인 경우 422 에러
    """
    return controller.register(request)


@router.post("/login", response_model=Token)
def login(
    request: LoginUserRequest, controller: UserController = Depends(get_user_controller)
):
    """
    로그인

    이메일과 비밀번호로 로그인하고 JWT 토큰을 발급

    Args:
        request: 로그인 요청 데이터 (이메일, 비밀번호)
        controller: 사용자 컨트롤러

    Returns:
        Token: JWT 액세스 토큰

    Raises:
        HTTPException: 이메일 또는 비밀번호가 올바르지 않은 경우 401 에러
    """
    return controller.login(request)


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """
    로그아웃

    현재 인증된 사용자를 로그아웃

    Args:
        current_user: 현재 인증된 사용자
        controller: 사용자 컨트롤러

    Returns:
        dict: 로그아웃 성공 메시지

    Raises:
        HTTPException: 인증되지 않은 경우 401 에러
    """
    return controller.logout(current_user)


@router.get("/{id}", response_model=UserResponse)
def get_profile(id: int, controller: UserController = Depends(get_user_controller)):
    """
    사용자 프로필 조회

    사용자 ID로 프로필 정보를 조회

    Args:
        id: 조회할 사용자 ID
        controller: 사용자 컨트롤러

    Returns:
        UserResponse: 사용자 프로필 정보

    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 404 에러
    """
    return controller.get_profile(id)


@router.patch("/{id}", response_model=UserResponse)
def update_profile(
    id: int,
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """
    회원정보수정

    인증된 사용자가 자신의 프로필 정보를 수정

    Args:
        id: 수정할 사용자 ID
        request: 사용자 정보 수정 요청 데이터
        current_user: 현재 인증된 사용자
        controller: 사용자 컨트롤러

    Returns:
        UserResponse: 수정된 사용자 정보

    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 404 에러
        HTTPException: 권한이 없는 경우 403 에러
    """
    return controller.update_profile(id, request, current_user)


@router.patch("/{id}/password", status_code=status.HTTP_200_OK)
def change_password(
    id: int,
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """
    비밀번호 변경

    인증된 사용자가 자신의 비밀번호를 변경

    Args:
        id: 비밀번호를 변경할 사용자 ID
        request: 비밀번호 변경 요청 데이터 (현재 비밀번호, 새 비밀번호)
        current_user: 현재 인증된 사용자
        controller: 사용자 컨트롤러

    Returns:
        dict: 비밀번호 변경 성공 메시지

    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 404 에러
        HTTPException: 권한이 없는 경우 403 에러
        HTTPException: 현재 비밀번호가 일치하지 않는 경우 400 에러
    """
    return controller.change_password(id, request, current_user)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    id: int,
    current_user: User = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller),
):
    """
    회원 탈퇴

    인증된 사용자가 자신의 계정을 삭제

    Args:
        id: 삭제할 사용자 ID
        current_user: 현재 인증된 사용자
        controller: 사용자 컨트롤러

    Returns:
        None: 204 No Content 응답

    Raises:
        HTTPException: 사용자를 찾을 수 없는 경우 404 에러
        HTTPException: 권한이 없는 경우 403 에러
    """
    controller.delete_account(id, current_user)
