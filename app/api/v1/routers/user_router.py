from fastapi import APIRouter, Depends, status
from app.api.v1.controllers.user_controller import UserController
from app.models.user_model import UserModel
from app.dependencies import get_user_model
from app.schemas.user_schema import (
    RegisterUserRequest,
    LoginUserRequest,
    UpdateUserRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def get_user_controller(
    user_model: UserModel = Depends(get_user_model)
) -> UserController:
    """사용자 컨트롤러 의존성 주입

    Args:
        user_model: 사용자 모델 (의존성 주입)

    Returns:
        UserController: 사용자 컨트롤러 인스턴스
    """
    return UserController(user_model)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    request: RegisterUserRequest,
    controller: UserController = Depends(get_user_controller),
):
    """
        회원가입

    Args:

        request: 회원가입 요청 정보
            - email: 사용자 이메일
            - password: 비밀번호 (6-20자)
            - nick_name: 닉네임 (2-20자)
            - image_url: 프로필 이미지 URL (선택)

    Returns:

        UserResponse: 생성된 사용자 정보

    Raises:

        DuplicateException: 이미 존재하는 이메일인 경우
    """
    return controller.register(request)


@router.post("/login", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def login_user(
    request: LoginUserRequest, controller: UserController = Depends(get_user_controller)
):
    """
        로그인

    인증 없이 이메일/비밀번호 검증만 수행하고 사용자 정보를 반환합니다.
    실제 세션이나 토큰은 생성되지 않습니다.

    Args:

        request: 로그인 요청 정보
            - email: 사용자 이메일
            - password: 비밀번호

    Returns:

        UserResponse: 로그인된 사용자 정보

    Raises:

        UnauthorizedException: 이메일 또는 비밀번호가 일치하지 않는 경우
    """
    return controller.login(request)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(controller: UserController = Depends(get_user_controller)):
    """
        로그아웃

    Returns:

        dict: 성공 메시지
    """
    return controller.logout()


@router.get(
    "/{user_id}/profile", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def get_user_profile(
    user_id: int, controller: UserController = Depends(get_user_controller)
):
    """프로필 조회

        user_id로 프로필을 조회합니다.

    Args:

        user_id: 사용자 ID

    Returns:

        UserResponse: 사용자 정보

    Raises:

        NotFoundException: 사용자를 찾을 수 없는 경우
    """
    return controller.get_profile(user_id)


@router.patch(
    "/{user_id}/profile", response_model=UserResponse, status_code=status.HTTP_200_OK
)
async def update_user_profile(
    user_id: int,
    request: UpdateUserRequest,
    controller: UserController = Depends(get_user_controller),
):
    """프로필 수정

        user_id로 프로필을 수정합니다.

    Args:

        user_id: 사용자 ID
        request: 프로필 수정 요청 정보
            - nick_name: 닉네임 (2-20자, 선택)
            - image_url: 프로필 이미지 URL (선택)

    Returns:

        UserResponse: 수정된 사용자 정보

    Raises:

        NotFoundException: 사용자를 찾을 수 없는 경우
    """
    return controller.update_profile(user_id, request)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int, controller: UserController = Depends(get_user_controller)
):
    """회원 탈퇴

    Args:

        user_id: 사용자 ID

    Returns:

        dict: 성공 메시지

    Raises:

        NotFoundException: 사용자를 찾을 수 없는 경우
    """
    return controller.delete_user(user_id)
