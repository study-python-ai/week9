from re import match
from typing import Annotated, Optional

from pydantic import AfterValidator, BaseModel, Field


def validate_email(value: str) -> str:
    """이메일 검증"""
    if not value:
        raise ValueError("이메일은 필수 입력 항목입니다.")
    if not match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
        raise ValueError("올바른 이메일 형식이 아닙니다.")
    return value


def validate_password(value: str) -> str:
    """비밀번호 검증"""
    if not value:
        raise ValueError("비밀번호는 필수 입력 항목입니다.")
    if len(value) < 6 or len(value) > 20:
        raise ValueError("비밀번호는 6자 이상 20자 이하이어야 합니다.")
    return value


def validate_nick_name(value: str) -> str:
    """닉네임 검증"""
    if not value:
        raise ValueError("닉네임은 필수 입력 항목입니다.")
    if len(value) < 2 or len(value) > 20:
        raise ValueError("닉네임은 2자 이상 20자 이하이어야 합니다.")
    return value


EmailStr = Annotated[str, AfterValidator(validate_email)]
PasswordStr = Annotated[str, AfterValidator(validate_password)]
NickNameStr = Annotated[str, AfterValidator(validate_nick_name)]


class RegisterUserRequest(BaseModel):
    """회원가입 요청 DTO"""

    email: EmailStr = Field(..., description="사용자 이메일")
    password: PasswordStr = Field(..., description="비밀번호 (6-20자)")
    nick_name: NickNameStr = Field(..., description="닉네임 (2-20자)")
    image_url: Optional[str] = Field(None, description="프로필 이미지 URL")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123",
                "nick_name": "홍길동",
                "image_url": "https://example.com/profile.jpg",
            }
        }


class LoginUserRequest(BaseModel):
    """로그인 요청 DTO"""

    email: EmailStr = Field(..., description="사용자 이메일")
    password: str = Field(..., description="비밀번호")

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com", "password": "password123"}
        }


class UpdateUserRequest(BaseModel):
    """프로필 수정 요청 DTO"""

    nick_name: Optional[NickNameStr] = Field(None, description="닉네임 (2-20자)")
    image_url: Optional[str] = Field(None, description="프로필 이미지 URL")

    class Config:
        json_schema_extra = {
            "example": {
                "nick_name": "새로운닉네임",
                "image_url": "https://example.com/new-profile.jpg",
            }
        }


class ChangePasswordRequest(BaseModel):
    """비밀번호 변경 요청 DTO"""

    current_password: str = Field(..., description="현재 비밀번호")
    new_password: PasswordStr = Field(..., description="새 비밀번호 (6-20자)")

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newpassword123",
            }
        }


class UserResponse(BaseModel):
    """사용자 응답 DTO"""

    id: int
    email: str
    nick_name: str
    image_url: Optional[str] = None
    del_yn: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "nick_name": "홍길동",
                "image_url": "https://example.com/profile.jpg",
                "del_yn": "N",
                "created_at": "2025-01-13 10:30:00",
                "updated_at": "2025-01-13 10:30:00",
            }
        }
