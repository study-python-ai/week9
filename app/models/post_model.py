from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.comment_model import Comment
    from app.models.user_model import User


class DeleteStatus(str, Enum):
    """삭제 상태"""

    NOT_DELETED = "N"
    DELETED = "Y"


class Post(Base, TimestampMixin, SoftDeleteMixin):
    """게시글 모델"""

    __tablename__ = "tb_post"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("tb_user.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(26), nullable=False)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)

    author: Mapped["User"] = relationship(
        "User", back_populates="posts", foreign_keys=[author_id]
    )
    comments: Mapped[List["Comment"]] = relationship(
        "Comment", back_populates="post", foreign_keys="Comment.post_id"
    )

    @property
    def images(self) -> List[str]:
        """게시글 이미지 URL 목록 조회"""
        from sqlalchemy.orm import object_session

        from app.models.image_model import ImageModel

        session = object_session(self)
        if not session:
            return []

        image_model = ImageModel(session)
        images = image_model.find_post_images(self.id)
        return [img.url for img in images]

    @property
    def img_url(self) -> Optional[str]:
        """첫 번째 이미지 URL 조회 (하위 호환성)"""
        images = self.images
        return images[0] if images else None

    def _change_title(self, title: str) -> None:
        """제목 변경"""
        self.title = title

    def _change_content(self, content: str) -> None:
        """내용 변경"""
        self.content = content

    def delete(self) -> None:
        """게시글 논리적 삭제"""
        self.del_yn = DeleteStatus.DELETED.value

    def change_post(self, title: Optional[str], content: Optional[str]) -> 'Post':
        """게시글 정보 변경"""
        if title is not None:
            self._change_title(title)

        if content is not None:
            self._change_content(content)

        self.updated_at = datetime.now().isoformat()
        return self


class PostModel:
    """게시글 모델 관리"""

    def __init__(self, db: Session):
        self.db = db

    def find_posts(
        self, cursor_id: Optional[int] = None, limit: int = 10
    ) -> List[Post]:
        """전체 게시글 목록 조회

        Args:
            cursor_id (int, optional): 커서 ID. 페이지 네비게이션에 사용
            limit (int, optional): 조회할 게시글 수.

        Returns:
            List[Post]: 게시글 목록
        """
        stmt = select(Post).where(Post.active_filter())

        if cursor_id is not None:
            stmt = stmt.where(Post.id < cursor_id)

        stmt = stmt.order_by(Post.id.desc()).limit(limit)

        return list(self.db.execute(stmt).scalars().all())

    def find_by_id(self, post_id: int) -> Optional[Post]:
        """게시글 단건 조회

        Args:
            post_id (int): 게시글 ID

        Returns:
            Optional[Post]: 게시글
        """
        stmt = select(Post).where(Post.active_filter(), Post.id == post_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, title: str, content: str, author_id: int) -> Post:
        """게시글 생성"""
        post = Post(author_id=author_id, title=title, content=content)

        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)

        return post

    def update(
        self, id: int, title: Optional[str] = None, content: Optional[str] = None
    ) -> Optional[Post]:
        """게시글 수정"""
        post = self.find_by_id(id)

        if not post:
            return None

        post.change_post(title, content)
        self.db.commit()
        self.db.refresh(post)

        return post

    def delete(self, id: int) -> bool:
        """게시글 삭제 (논리적 삭제 - del_yn='Y')"""
        post = self.find_by_id(id)

        if not post:
            return False

        post.delete()
        self.db.commit()
        return True

    def get_post_stats(self, post_id: int) -> Dict[str, int]:
        """게시글 통계 조회 (조회수, 좋아요 수, 댓글 수)

        Args:
            post_id: 게시글 ID

        Returns:
            Dict[str, int]: {"view_count": int, "like_count": int, "comment_count": int}
        """
        from app.models.comment_model import Comment
        from app.models.like_model import Like
        from app.models.view_model import View

        view_count_stmt = select(func.count(View.id)).where(View.post_id == post_id)
        view_count = self.db.execute(view_count_stmt).scalar() or 0

        like_count_stmt = select(func.count(Like.id)).where(Like.post_id == post_id)
        like_count = self.db.execute(like_count_stmt).scalar() or 0

        comment_count_stmt = select(func.count(Comment.id)).where(
            Comment.post_id == post_id, Comment.active_filter()
        )
        comment_count = self.db.execute(comment_count_stmt).scalar() or 0

        return {
            "view_count": view_count,
            "like_count": like_count,
            "comment_count": comment_count,
        }

    def add_view(self, post_id: int, user_id: int) -> None:
        """조회수 추가 (Aggregate 패턴)

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID
        """
        from app.models.view_model import View

        stmt = select(View).where(View.post_id == post_id, View.user_id == user_id)
        existing_view = self.db.execute(stmt).scalar_one_or_none()

        if not existing_view:
            view = View(post_id=post_id, user_id=user_id)
            self.db.add(view)
            self.db.commit()

    def add_like(self, post_id: int, user_id: int) -> bool:
        """좋아요 추가 (Aggregate 패턴)

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID

        Returns:
            bool: 추가 성공 여부 (이미 좋아요한 경우 False)
        """
        from app.models.like_model import Like

        stmt = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        existing_like = self.db.execute(stmt).scalar_one_or_none()

        if existing_like:
            return False

        like = Like(post_id=post_id, user_id=user_id)
        self.db.add(like)
        self.db.commit()
        return True

    def remove_like(self, post_id: int, user_id: int) -> bool:
        """좋아요 취소 (Aggregate 패턴)

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID

        Returns:
            bool: 취소 성공 여부 (좋아요하지 않은 경우 False)
        """
        from app.models.like_model import Like

        stmt = select(Like).where(Like.post_id == post_id, Like.user_id == user_id)
        like = self.db.execute(stmt).scalar_one_or_none()

        if not like:
            return False

        self.db.delete(like)
        self.db.commit()
        return True

    def get_comments(self, post_id: int) -> List["Comment"]:
        """게시글의 댓글 목록 조회

        Args:
            post_id: 게시글 ID

        Returns:
            List[Comment]: 댓글 목록
        """
        from app.models.comment_model import Comment

        stmt = select(Comment).where(
            Comment.active_filter(), Comment.post_id == post_id
        )
        return list(self.db.execute(stmt).scalars().all())

    def add_comment(self, post_id: int, author_id: int, content: str) -> "Comment":
        """댓글 추가 (Aggregate 패턴)

        Args:
            post_id: 게시글 ID
            author_id: 작성자 ID
            content: 댓글 내용

        Returns:
            Comment: 생성된 댓글
        """
        from app.models.comment_model import Comment

        comment = Comment(post_id=post_id, author_id=author_id, content=content)

        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def update_comment(
        self, post_id: int, comment_id: int, content: str, author_id: int
    ) -> Optional["Comment"]:
        """댓글 수정 (Aggregate 패턴, 권한 체크 포함)

        Args:
            post_id: 게시글 ID
            comment_id: 댓글 ID
            content: 수정할 내용
            author_id: 작성자 ID (권한 체크용)

        Returns:
            Optional[Comment]: 수정된 댓글 (권한 없거나 없으면 None)
        """
        from app.models.comment_model import Comment

        stmt = select(Comment).where(Comment.active_filter(), Comment.id == comment_id)
        comment = self.db.execute(stmt).scalar_one_or_none()

        if not comment or comment.post_id != post_id or comment.author_id != author_id:
            return None

        comment.content = content
        comment.updated_at = datetime.now().isoformat()
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete_comment(self, post_id: int, comment_id: int, author_id: int) -> bool:
        """댓글 삭제 (Aggregate 패턴, 권한 체크 포함)

        Args:
            post_id: 게시글 ID
            comment_id: 댓글 ID
            author_id: 작성자 ID (권한 체크용)

        Returns:
            bool: 삭제 성공 여부
        """
        from app.models.comment_model import Comment

        stmt = select(Comment).where(Comment.active_filter(), Comment.id == comment_id)
        comment = self.db.execute(stmt).scalar_one_or_none()

        if not comment or comment.post_id != post_id or comment.author_id != author_id:
            return False

        comment.delete()
        self.db.commit()
        return True
