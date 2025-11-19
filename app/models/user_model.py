from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.comment_model import Comment
    from app.models.post_model import Post


class DeleteStatus(str, Enum):
    """삭제 상태"""

    NOT_DELETED = "N"
    DELETED = "Y"


class User(Base, TimestampMixin, SoftDeleteMixin):
    """사용자 모델"""

    __tablename__ = "tb_user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    nick_name: Mapped[str] = mapped_column(String(100), nullable=False)

    posts: Mapped[List["Post"]] = relationship(
        "Post", back_populates="author", foreign_keys="Post.author_id"
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="author", foreign_keys="Comment.author_id"
    )

    @property
    def image_url(self) -> Optional[str]:
        """프로필 이미지 URL 조회"""
        from sqlalchemy.orm import object_session

        from app.models.image_model import ImageModel

        session = object_session(self)
        if not session:
            return None

        image_model = ImageModel(session)
        image = image_model.find_user_profile_image(self.id)
        return image.url if image else None

    def _change_nick_name(self, nick_name: str) -> None:
        """닉네임 변경"""
        self.nick_name = nick_name

    def _change_password(self, password: str) -> None:
        """비밀번호 변경"""
        self.password = password

    def delete(self) -> None:
        """사용자 논리적 삭제"""
        self.del_yn = DeleteStatus.DELETED.value

    def change_user(
        self, nick_name: Optional[str] = None, password: Optional[str] = None
    ) -> 'User':
        """사용자 정보 변경"""
        if nick_name is not None:
            self._change_nick_name(nick_name)

        if password is not None:
            self._change_password(password)

        self.updated_at = datetime.now().isoformat()
        return self


class UserModel:
    """사용자 데이터 관리"""

    def __init__(self, db: Session):
        self.db = db

    def find_users(self) -> List[User]:
        """전체 사용자 목록 조회

        Returns:
            List[User]: 활성 사용자 목록
        """
        stmt = select(User).where(User.active_filter())
        return list(self.db.execute(stmt).scalars().all())

    def create(self, email: str, password: str, nick_name: str) -> User:
        """사용자 생성

        Args:
            email: 이메일
            password: 비밀번호
            nick_name: 닉네임

        Returns:
            User: 생성된 사용자
        """
        user = User(email=email, password=password, nick_name=nick_name)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def find_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회

        Args:
            email: 이메일

        Returns:
            Optional[User]: 사용자 (없으면 None)
        """
        stmt = select(User).where(User.active_filter(), User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[User]: 사용자 (없으면 None)
        """
        stmt = select(User).where(User.active_filter(), User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

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
        password: Optional[str] = None,
    ) -> Optional[User]:
        """사용자 정보 수정

        Args:
            user_id: 사용자 ID
            nick_name: 닉네임 (선택)
            password: 비밀번호 (선택)

        Returns:
            Optional[User]: 수정된 사용자 (없으면 None)
        """
        user = self.find_by_id(user_id)

        if not user:
            return None

        user.change_user(nick_name, password)
        self.db.commit()
        self.db.refresh(user)

        return user

    def delete(self, user_id: int) -> bool:
        """사용자 삭제 (논리적 삭제 - del_yn='Y')

        Args:
            user_id: 사용자 ID

        Returns:
            bool: 삭제 성공 여부
        """
        user = self.find_by_id(user_id)

        if not user:
            return False

        user.delete()
        self.db.commit()
        return True
