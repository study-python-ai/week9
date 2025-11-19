from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.models.base import Base


class View(Base):
    """조회 이력"""

    __tablename__ = "tb_view"

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
        UniqueConstraint("post_id", "user_id", name="uq_view_post_user"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )


class ViewModel:
    """조회 이력 관리"""

    def __init__(self, db: Session):
        self.db = db

    def add_view(self, post_id: int, user_id: int) -> Optional[View]:
        """조회 이력 추가

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID

        Returns:
            Optional[View]: 추가된 조회 이력 (이미 조회한 경우 None)
        """
        if self.has_viewed(post_id, user_id):
            return None

        view = View(post_id=post_id, user_id=user_id)
        self.db.add(view)
        self.db.commit()
        self.db.refresh(view)
        return view

    def has_viewed(self, post_id: int, user_id: int) -> bool:
        """조회 여부 확인

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID

        Returns:
            bool: 조회 여부
        """
        stmt = select(View).where(View.post_id == post_id, View.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def count_by_post_id(self, post_id: int) -> int:
        """게시글의 조회 수 조회

        Args:
            post_id: 게시글 ID

        Returns:
            int: 조회 수 (고유 사용자 수)
        """
        from sqlalchemy import func

        stmt = select(func.count(View.id)).where(View.post_id == post_id)
        return self.db.execute(stmt).scalar() or 0
