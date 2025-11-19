from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, select, func
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.post_model import Post


class DeleteStatus(str, Enum):
    """삭제 상태"""

    NOT_DELETED = "N"
    DELETED = "Y"


class Comment(Base, TimestampMixin, SoftDeleteMixin):
    """댓글 모델"""

    __tablename__ = "tb_comment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("tb_post.id"), nullable=False, index=True
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("tb_user.id"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(String(1000), nullable=False)

    author: Mapped["User"] = relationship(
        "User", back_populates="comments", foreign_keys=[author_id]
    )
    post: Mapped["Post"] = relationship(
        "Post", back_populates="comments", foreign_keys=[post_id]
    )

    @property
    def img_url(self) -> Optional[str]:
        """댓글 작성자의 프로필 이미지 URL (하위 호환성)"""
        return self.author.image_url if self.author else None

    def delete(self) -> None:
        """댓글 논리적 삭제"""
        self.del_yn = DeleteStatus.DELETED.value


class CommentModel:
    """댓글 데이터 관리"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self, post_id: int, author_id: int, content: str
    ) -> Comment:
        """댓글 생성

        Args:
            post_id: 게시글 ID
            author_id: 작성자 ID
            content: 댓글 내용

        Returns:
            Comment: 생성된 댓글
        """
        comment = Comment(
            post_id=post_id, author_id=author_id, content=content
        )

        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def find_by_id(self, comment_id: int) -> Optional[Comment]:
        """ID로 댓글 조회

        Args:
            comment_id: 댓글 ID

        Returns:
            Optional[Comment]: 댓글 (없으면 None)
        """
        stmt = select(Comment).where(Comment.active_filter(), Comment.id == comment_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_by_post_id(
        self, post_id: int, cursor_id: Optional[int] = None, limit: int = 10
    ) -> List[Comment]:
        """게시글의 댓글 조회 (커서 페이지네이션 지원)

        Args:
            post_id: 게시글 ID
            cursor_id: 커서 ID (이전 페이지 마지막 댓글 ID)
            limit: 조회할 댓글 수

        Returns:
            List[Comment]: 댓글 목록 (ID 내림차순)
        """
        stmt = select(Comment).where(
            Comment.active_filter(), Comment.post_id == post_id
        )

        if cursor_id is not None:
            stmt = stmt.where(Comment.id < cursor_id)

        stmt = stmt.order_by(Comment.id.desc()).limit(limit)

        return list(self.db.execute(stmt).scalars().all())

    def delete(self, comment_id: int) -> bool:
        """댓글 삭제 (논리적 삭제 - del_yn='Y')

        Args:
            comment_id: 댓글 ID

        Returns:
            bool: 삭제 성공 여부
        """
        comment = self.find_by_id(comment_id)
        if not comment:
            return False

        comment.delete()
        self.db.commit()
        return True

    def exists_by_id(self, comment_id: int) -> bool:
        """댓글 존재 여부 확인

        Args:
            comment_id: 댓글 ID

        Returns:
            bool: 존재 여부
        """
        return self.find_by_id(comment_id) is not None

    def count_by_post_id(self, post_id: int) -> int:
        """게시글의 댓글 수 조회

        Args:
            post_id: 게시글 ID

        Returns:
            int: 댓글 수
        """
        stmt = select(func.count(Comment.id)).where(
            Comment.active_filter(), Comment.post_id == post_id
        )
        return self.db.execute(stmt).scalar() or 0

    def update(self, comment_id: int, content: str) -> Optional[Comment]:
        """댓글 내용 수정

        Args:
            comment_id: 댓글 ID
            content: 수정할 내용

        Returns:
            Optional[Comment]: 수정된 댓글 (없으면 None)
        """
        comment = self.find_by_id(comment_id)
        if not comment:
            return None

        comment.content = content
        comment.updated_at = datetime.now().isoformat()
        self.db.commit()
        self.db.refresh(comment)
        return comment
