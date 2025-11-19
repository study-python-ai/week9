from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.models.base import Base


class Like(Base):
    """좋아요"""

    __tablename__ = "tb_like"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("tb_post.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("tb_user.id"), nullable=False, index=True
    )
    created_at: Mapped[str] = mapped_column(
        String, default=lambda: datetime.now().isoformat(), nullable=False
    )

    __table_args__ = (
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )


class LikeModel:
    """좋아요 모델"""

    def __init__(self, db: Session):
        self.db = db

    def add_like(self, post_id: int, user_id: int) -> Optional[Like]:
        """좋아요 추가

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID

        Returns:
            Optional[Like]: 추가된 좋아요 (이미 존재하면 None)
        """
        if self.has_liked(post_id, user_id):
            return None

        like = Like(post_id=post_id, user_id=user_id)
        self.db.add(like)
        self.db.commit()
        self.db.refresh(like)
        return like

    def remove_like(self, post_id: int, user_id: int) -> bool:
        """좋아요 제거

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID

        Returns:
            bool: 제거 성공 여부
        """
        stmt = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        like = self.db.execute(stmt).scalar_one_or_none()

        if not like:
            return False

        self.db.delete(like)
        self.db.commit()
        return True

    def has_liked(self, post_id: int, user_id: int) -> bool:
        """좋아요 여부 확인

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID

        Returns:
            bool: 좋아요 여부
        """
        stmt = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def get_likes_by_post(self, post_id: int) -> List[Like]:
        """게시글의 좋아요 목록 조회

        Args:
            post_id: 게시글 ID

        Returns:
            List[Like]: 좋아요 목록
        """
        stmt = select(Like).where(Like.post_id == post_id)
        return list(self.db.execute(stmt).scalars().all())
