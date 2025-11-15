from app.schemas.user_schema import (
    RegisterUserRequest,
    LoginUserRequest,
    UpdateUserRequest,
    UserResponse,
)
from app.models.user_model import UserModel
from app.common.exceptions import UnauthorizedException
from app.common.validators import get_or_raise, ensure_unique


class UserController:
    """사용자 관련 비즈니스 로직 처리"""

    def __init__(self, user_model: UserModel):
        self.user_model = user_model

    def register(self, request: RegisterUserRequest) -> UserResponse:
        """회원가입 처리

        Args:
            request: 회원가입 요청
                - email: 사용자 이메일
                - password: 비밀번호
                - nick_name: 닉네임
                - image_url: 프로필 이미지 URL (선택)

        Returns:
            UserResponse: 생성된 사용자

        Raises:
            DuplicateException: 이미 존재하는 이메일인 경우
        """
        ensure_unique(
            self.user_model.exists_by_email(request.email),
            "이미 존재하는 이메일입니다.",
        )

        user = self.user_model.create(
            email=request.email,
            password=request.password,
            nick_name=request.nick_name,
            image_url=request.image_url,
        )
        return UserResponse.model_validate(user)

    def login(self, request: LoginUserRequest) -> UserResponse:
        """로그인 처리 (더미 구현 - 이메일/비밀번호 검증만 수행)

        Args:
            request: 로그인 요청
                - email: 사용자 이메일
                - password: 비밀번호

        Returns:
            UserResponse: 로그인된 사용자

        Raises:
            UnauthorizedException: 이메일 또는 비밀번호가 일치하지 않는 경우
        """
        user = self.user_model.find_by_email(request.email)

        if user is None or user.password != request.password:
            raise UnauthorizedException("이메일 또는 비밀번호가 일치하지 않습니다.")

        return UserResponse.model_validate(user)

    def logout(self) -> dict:
        """로그아웃 처리 (더미 구현 - 항상 성공)

        Returns:
            dict: 성공 메시지
        """
        return {"message": "로그아웃되었습니다."}

    def get_profile(self, user_id: int) -> UserResponse:
        """프로필 조회

        Args:
            user_id: 사용자 ID

        Returns:
            UserResponse: 사용자

        Raises:
            NotFoundException: 사용자를 찾을 수 없는 경우
        """
        user = get_or_raise(
            self.user_model.find_by_id(user_id), "사용자를 찾을 수 없습니다."
        )

        return UserResponse.model_validate(user)

    def update_profile(self, user_id: int, request: UpdateUserRequest) -> UserResponse:
        """프로필 수정

        Args:
            user_id: 사용자 ID
            request: 프로필 수정 요청
                - nick_name: 닉네임 (선택)
                - image_url: 프로필 이미지 URL (선택)

        Returns:
            UserResponse: 수정된 사용자

        Raises:
            NotFoundException: 사용자를 찾을 수 없는 경우
        """
        user = get_or_raise(
            self.user_model.update(
                user_id=user_id,
                nick_name=request.nick_name,
                image_url=request.image_url,
            ),
            "사용자를 찾을 수 없습니다.",
        )

        return UserResponse.model_validate(user)

    def delete_user(self, user_id: int) -> dict:
        """회원 탈퇴

        Args:
            user_id: 사용자 ID

        Returns:
            dict: 성공 메시지

        Raises:
            NotFoundException: 사용자를 찾을 수 없는 경우
        """
        get_or_raise(self.user_model.find_by_id(user_id), "사용자를 찾을 수 없습니다.")

        self.user_model.delete(user_id)

        return {"message": "회원 탈퇴가 완료되었습니다."}
