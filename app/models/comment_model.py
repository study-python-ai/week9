from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Comment:
    """댓글 모델"""
    id: int
    post_id: int
    author_id: int
    content: str
    img_url: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class CommentModel:
    """댓글 데이터 관리 (인메모리 - 싱글톤)"""

    _instance = None
    _comments: List[Comment] = []
    _next_id: int = 1

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def create(self, post_id: int, author_id: int, content: str, img_url: Optional[str] = None) -> Comment:
        """댓글 생성"""
        comment = Comment(
            id=self._next_id,
            post_id=post_id,
            author_id=author_id,
            content=content,
            img_url=img_url
        )
        self._comments.append(comment)
        self._next_id += 1
        return comment

    def find_by_id(self, comment_id: int) -> Optional[Comment]:
        """ID로 댓글 조회"""
        return next((comment for comment in self._comments if comment.id == comment_id), None)

    def find_by_post_id(self, post_id: int) -> List[Comment]:
        """게시글의 모든 댓글 조회"""
        return [comment for comment in self._comments if comment.post_id == post_id]

    def delete(self, comment_id: int) -> bool:
        """댓글 삭제 (물리적 삭제)"""
        comment = self.find_by_id(comment_id)
        if not comment:
            return False

        self._comments = [c for c in self._comments if c.id != comment_id]
        return True

    def exists_by_id(self, comment_id: int) -> bool:
        """댓글 존재 여부 확인"""
        return self.find_by_id(comment_id) is not None

    def count_by_post_id(self, post_id: int) -> int:
        """게시글의 댓글 수 조회"""
        return len(self.find_by_post_id(post_id))

    def update(self, comment_id: int, content: str) -> Optional[Comment]:
        """댓글 내용 수정"""
        comment = self.find_by_id(comment_id)
        if not comment:
            return None

        comment.content = content
        return comment
