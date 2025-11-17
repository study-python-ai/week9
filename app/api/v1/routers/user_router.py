from fastapi import APIRouter, Depends, Request, status

from app.api.v1.controllers.user_controller import UserController

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def get_user_controller() -> UserController:
    """
        의존성 주입

    Returns:
        UserController: 사용자 컨트롤러
    """
    return UserController()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request, controller: UserController = Depends(get_user_controller)
):
    """회원가입"""
    return controller.register(request)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(
    request: Request, controller: UserController = Depends(get_user_controller)
):
    """로그인"""
    return controller.login(request)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(controller: UserController = Depends(get_user_controller)):
    """로그아웃"""
    return controller.logout()


@router.get("/{user_id}/profile", status_code=status.HTTP_200_OK)
async def get_user_profile(
    user_id: int, controller: UserController = Depends(get_user_controller)
):
    """프로필 조회"""
    return controller.get_profile(user_id)


@router.patch("/{user_id}/profile", status_code=status.HTTP_200_OK)
async def update_user_profile(
    user_id: int,
    request: Request,
    controller: UserController = Depends(get_user_controller),
):
    """프로필 수정"""
    return controller.update_profile(user_id, request)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int, controller: UserController = Depends(get_user_controller)
):
    """회원 탈퇴"""
    return controller.delete_user(user_id)
