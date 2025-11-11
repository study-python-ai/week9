from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class User:
    """사용자 모델"""
    id: int
    email: str
    password: str
    nick_name: str
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class UserModel:
    """사용자 데이터 관리 (인메모리)"""

    def __init__(self):
        self._users: List[User] = []
        self._next_id: int = 1

    def create(self, email: str, password: str, nick_name: str, image_url: Optional[str] = None) -> User:
        """사용자 생성"""
        user = User(
            id=self._next_id,
            email=email,
            password=password,
            nick_name=nick_name,
            image_url=image_url
        )
        self._users.append(user)
        self._next_id += 1
        return user

    def find_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return next((user for user in self._users if user.email == email and user.is_active), None)

    def find_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return next((user for user in self._users if user.id == user_id and user.is_active), None)

    def exists_by_email(self, email: str) -> bool:
        """이메일 존재 여부 확인"""
        return self.find_by_email(email) is not None

    def update(self, user_id: int, nick_name: Optional[str] = None, image_url: Optional[str] = None) -> Optional[User]:
        """사용자 정보 수정"""
        user = self.find_by_id(user_id)
        if not user:
            return None

        if nick_name is not None:
            user.nick_name = nick_name
        if image_url is not None:
            user.image_url = image_url

        return user

    def delete(self, user_id: int) -> bool:
        """사용자 삭제 (소프트 삭제)"""
        user = self.find_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        return True

    def get_all(self) -> List[User]:
        """전체 사용자 목록 조회 (활성 사용자만)"""
        return [user for user in self._users if user.is_active]
