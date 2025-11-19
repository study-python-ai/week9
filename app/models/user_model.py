from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class DeleteStatus(str, Enum):
    """삭제 상태"""

    NOT_DELETED = "N"
    DELETED = "Y"


@dataclass
class User:
    """사용자 모델"""

    id: int = 0
    email: str = ""
    password: str = ""
    nick_name: str = ""
    image_url: Optional[str] = None
    del_yn: str = field(default=DeleteStatus.NOT_DELETED.value)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def _change_nick_name(self, nick_name: str) -> None:
        """닉네임 변경"""
        self.nick_name = nick_name

    def _change_image_url(self, image_url: str) -> None:
        """이미지 URL 변경"""
        self.image_url = image_url

    def _change_password(self, password: str) -> None:
        """비밀번호 변경"""
        self.password = password

    def delete(self) -> None:
        """사용자 논리적 삭제"""
        self.del_yn = DeleteStatus.DELETED.value

    def change_user(
        self,
        nick_name: Optional[str] = None,
        image_url: Optional[str] = None,
        password: Optional[str] = None,
    ) -> 'User':
        """사용자 정보 변경"""
        if nick_name is not None:
            self._change_nick_name(nick_name)

        if image_url is not None:
            self._change_image_url(image_url)

        if password is not None:
            self._change_password(password)

        self.updated_at = datetime.now().isoformat()
        return self


@dataclass
class Users:
    """사용자 DB 모델"""

    __tablename__ = 'tb_user'

    def __init__(self, users: List[User], condition=None):
        self._users = users
        self.condition = condition

    def __iter__(self):
        return iter(self._users)

    def __len__(self):
        return len(self._users)

    def __getitem__(self, index):
        return self._users[index]

    def __add__(self, other):
        return Users(self._users + other._users)

    def append(self, user: User, next_id: int) -> None:
        """사용자 추가

        Args:
            user: 추가할 사용자
            next_id: 할당할 ID
        """
        user.id = next_id
        self._users.append(user)

    def get(self, condition) -> 'Users':
        """조건에 맞는 사용자 필터링"""
        users: List[User] = [user for user in self._users if condition(user)]
        return Users(users, condition=condition)

    def get_condition_not_delete(self, condition) -> 'Users':
        """비활성화되지 않은 사용자만 필터링"""
        return self.get(
            lambda user: user.del_yn == DeleteStatus.NOT_DELETED.value
            and condition(user)
        )

    def get_user(self, user_id: int) -> Optional[User]:
        """사용자 단건 조회"""
        users = self.get_condition_not_delete(lambda user: user.id == user_id)
        return users._users[0] if len(users) > 0 else None

    def to_list(self) -> List[User]:
        """사용자 리스트 반환"""
        return self._users


class UserModel:
    """사용자 데이터 관리"""

    def __init__(self):
        self._users: Users = Users([])
        self._next_id: int = 1

    def find_users(self) -> List[User]:
        """전체 사용자 목록 조회

        Returns:
            List[User]: 활성 사용자 목록
        """
        return self._users.get(
            lambda user: user.del_yn == DeleteStatus.NOT_DELETED.value
        ).to_list()

    def create(
        self, email: str, password: str, nick_name: str, image_url: Optional[str] = None
    ) -> User:
        """사용자 생성

        Args:
            email: 이메일
            password: 비밀번호
            nick_name: 닉네임
            image_url: 프로필 이미지 URL (선택)

        Returns:
            User: 생성된 사용자
        """
        user = User(
            email=email, password=password, nick_name=nick_name, image_url=image_url
        )

        self._users.append(user, self._next_id)
        self._next_id += 1

        return user

    def find_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회

        Args:
            email: 이메일

        Returns:
            Optional[User]: 사용자 (없으면 None)
        """
        users = self._users.get_condition_not_delete(lambda user: user.email == email)
        return users._users[0] if len(users) > 0 else None

    def find_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[User]: 사용자 (없으면 None)
        """
        return self._users.get_user(user_id)

    def exists_by_email(self, email: str) -> bool:
        """이메일 존재 여부 확인

        Args:
            email: 이메일

        Returns:
            bool: 존재 여부
        """
        return self.find_by_email(email) is not None

    def update(
        self,
        user_id: int,
        nick_name: Optional[str] = None,
        image_url: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Optional[User]:
        """사용자 정보 수정

        Args:
            user_id: 사용자 ID
            nick_name: 닉네임 (선택)
            image_url: 이미지 URL (선택)
            password: 비밀번호 (선택)

        Returns:
            Optional[User]: 수정된 사용자 (없으면 None)
        """
        user = self.find_by_id(user_id)

        if not user:
            return None

        return user.change_user(nick_name, image_url, password)

    def delete(self, user_id: int) -> bool:
        """사용자 삭제 (논리적 삭제 - del_yn='N')

        Args:
            user_id: 사용자 ID

        Returns:
            bool: 삭제 성공 여부
        """
        user = self.find_by_id(user_id)

        if not user:
            return False

        user.delete()
        return True
