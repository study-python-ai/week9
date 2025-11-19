from app.core.exceptions.error_codes import ErrorCode
from app.core.exceptions.exceptions import (
    BadRequestException,
    ForbiddenException,
    UnauthorizedException,
)
from app.core.security.password import hash_password, verify_password
from app.core.security.security import create_access_token
from app.core.validators import ensure_unique, get_or_raise
from app.models.image_model import ImageModel, ImageType
from app.models.user_model import User, UserModel
from app.schemas import (
    ChangePasswordRequest,
    LoginUserRequest,
    RegisterUserRequest,
    Token,
    UpdateUserRequest,
    UserResponse,
)


class UserController:
    """v2 사용자 컨트롤러 클래스"""

    def __init__(self, user_model: UserModel, image_model: ImageModel):
        self.user_model = user_model
        self.image_model = image_model

    def register(self, request: RegisterUserRequest) -> UserResponse:
        """회원가입"""
        ensure_unique(
            self.user_model.exists_by_email(request.email),
            "이미 존재하는 이메일입니다.",
        )

        hashed_password = hash_password(request.password)

        user = self.user_model.create(
            email=request.email,
            password=hashed_password,
            nick_name=request.nick_name,
        )

        if request.image_id:
            temp_image = get_or_raise(
                self.image_model.find_by_id(request.image_id),
                "이미지를 찾을 수 없습니다.",
                error_code=ErrorCode.NOT_FOUND,
            )

            if temp_image.entity_type == "temp":
                self.image_model.update_entity(
                    image_id=request.image_id,
                    entity_type=ImageType.USER.value,
                    entity_id=user.id,
                    order=0,
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
        """프로필 수정"""
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
            ),
            "사용자 정보 수정에 실패했습니다.",
            error_code=ErrorCode.USER_NOT_FOUND,
        )

        if request.image_id:
            temp_image = get_or_raise(
                self.image_model.find_by_id(request.image_id),
                "이미지를 찾을 수 없습니다.",
                error_code=ErrorCode.NOT_FOUND,
            )

            if temp_image.uploaded_by == user_id and temp_image.entity_type == "temp":
                self.image_model.delete_by_entity(ImageType.USER.value, user_id)
                self.image_model.update_entity(
                    image_id=request.image_id,
                    entity_type=ImageType.USER.value,
                    entity_id=user_id,
                    order=0,
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
