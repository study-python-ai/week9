from app.common.error_codes import ErrorCode
from app.common.exceptions import (
    BadRequestException,
    ForbiddenException,
    UnauthorizedException,
)
from app.common.validators import ensure_unique, get_or_raise
from app.core.security import create_access_token
from app.models.user_model import User, UserModel
from app.schemas.common import (
    ChangePasswordRequest,
    LoginUserRequest,
    RegisterUserRequest,
    Token,
    UpdateUserRequest,
    UserResponse,
)
from app.utils.password import hash_password, verify_password


class UserController:
    """v2 사용자 컨트롤러 클래스"""

    def __init__(self, user_model: UserModel):
        self.user_model = user_model

    def register(self, request: RegisterUserRequest) -> UserResponse:
        """회원가입

        Args:
            request: 회원가입 요청

        Returns:
            UserResponse: 생성된 사용자

        Raises:
            DuplicateException: 이미 존재하는 이메일인 경우
        """
        ensure_unique(
            self.user_model.exists_by_email(request.email),
            "이미 존재하는 이메일입니다.",
        )

        hashed_password = hash_password(request.password)

        user = self.user_model.create(
            email=request.email,
            password=hashed_password,
            nick_name=request.nick_name,
            image_url=request.image_url,
        )

        return UserResponse.model_validate(user)

    def login(self, request: LoginUserRequest) -> Token:
        """로그인

        Args:
            request: 로그인 요청

        Returns:
            Token: JWT 액세스 토큰

        Raises:
            UnauthorizedException: 이메일 또는 비밀번호가 일치하지 않는 경우
        """
        user = self.user_model.find_by_email(request.email)

        if user is None:
            raise UnauthorizedException(
                "이메일 또는 비밀번호가 일치하지 않습니다.",
                error_code=ErrorCode.INVALID_CREDENTIALS,
            )

        if not verify_password(request.password, user.password):
            raise UnauthorizedException(
                "이메일 또는 비밀번호가 일치하지 않습니다.",
                error_code=ErrorCode.INVALID_CREDENTIALS,
            )

        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        return Token(access_token=access_token, token_type="bearer")

    def logout(self, current_user: User) -> dict:
        """로그아웃

        Args:
            current_user: 인증된 사용자

        Returns:
            dict: 성공 메시지
        """
        return {"message": "로그아웃되었습니다."}

    def get_profile(self, user_id: int) -> UserResponse:
        """프로필 조회

        Args:
            user_id: 사용자 ID

        Returns:
            UserResponse: 사용자 정보

        Raises:
            NotFoundException: 사용자를 찾을 수 없는 경우
        """
        user = get_or_raise(
            self.user_model.find_by_id(user_id), "사용자를 찾을 수 없습니다."
        )

        return UserResponse.model_validate(user)

    def update_profile(
        self, user_id: int, request: UpdateUserRequest, current_user: User
    ) -> UserResponse:
        """프로필 수정 (권한 확인)

        Args:
            user_id: 사용자 ID
            request: 수정 요청
            current_user: 인증된 사용자

        Returns:
            UserResponse: 수정된 사용자 정보

        Raises:
            NotFoundException: 사용자를 찾을 수 없는 경우
            ForbiddenException: 권한이 없는 경우
        """
        if current_user.id != user_id:
            raise ForbiddenException(
                "사용자 정보를 수정할 권한이 없습니다.",
                error_code=ErrorCode.USER_PERMISSION_DENIED,
            )

        get_or_raise(
            self.user_model.find_by_id(user_id),
            "사용자를 찾을 수 없습니다.",
            error_code=ErrorCode.USER_NOT_FOUND,
        )

        updated_user = get_or_raise(
            self.user_model.update(
                user_id=user_id,
                nick_name=request.nick_name,
                image_url=request.image_url,
            ),
            "사용자 정보 수정에 실패했습니다.",
            error_code=ErrorCode.USER_NOT_FOUND,
        )

        return UserResponse.model_validate(updated_user)

    def change_password(
        self, user_id: int, request: ChangePasswordRequest, current_user: User
    ) -> dict:
        """비밀번호 변경 (권한 확인)

        Args:
            user_id: 사용자 ID
            request: 비밀번호 변경 요청
            current_user: 인증된 사용자

        Returns:
            dict: 성공 메시지

        Raises:
            NotFoundException: 사용자를 찾을 수 없는 경우
            ForbiddenException: 권한이 없는 경우
            UnauthorizedException: 현재 비밀번호가 일치하지 않는 경우
            BadRequestException: 새 비밀번호가 현재 비밀번호와 동일한 경우
        """
        user = get_or_raise(
            self.user_model.find_by_id(user_id),
            "사용자를 찾을 수 없습니다.",
            error_code=ErrorCode.USER_NOT_FOUND,
        )

        if current_user.id != user_id:
            raise ForbiddenException(
                "본인의 비밀번호만 변경할 수 있습니다.",
                error_code=ErrorCode.USER_PERMISSION_DENIED,
            )

        if not verify_password(request.current_password, user.password):
            raise UnauthorizedException(
                "현재 비밀번호가 일치하지 않습니다.",
                error_code=ErrorCode.INVALID_CREDENTIALS,
            )

        if request.current_password == request.new_password:
            raise BadRequestException(
                "새 비밀번호는 현재 비밀번호와 달라야 합니다.",
                error_code=ErrorCode.INVALID_INPUT,
            )

        hashed_password = hash_password(request.new_password)
        self.user_model.update(user_id=user_id, password=hashed_password)

        return {"message": "비밀번호가 성공적으로 변경되었습니다."}

    def delete_account(self, user_id: int, current_user: User) -> None:
        """회원 탈퇴 (권한 확인)

        Args:
            user_id: 사용자 ID
            current_user: 인증된 사용자

        Raises:
            NotFoundException: 사용자를 찾을 수 없는 경우
            ForbiddenException: 권한이 없는 경우
        """
        user = get_or_raise(
            self.user_model.find_by_id(user_id),
            "사용자를 찾을 수 없습니다.",
            error_code=ErrorCode.USER_NOT_FOUND,
        )

        if current_user.id != user_id:
            raise ForbiddenException(
                "사용자를 삭제할 권한이 없습니다.",
                error_code=ErrorCode.USER_PERMISSION_DENIED,
            )

        self.user_model.delete(user.id)
        return None
