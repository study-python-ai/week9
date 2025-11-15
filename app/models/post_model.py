from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Post:
    """게시글 모델"""

    id: int
    title: str
    content: str
    author_id: int
    img_url: Optional[str] = None
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    del_yn: str = "N"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class PostModel:
    """게시글 데이터 관리 (인메모리)"""

    def __init__(self):
        self._posts: List[Post] = []
        self._next_id: int = 1

    def find_posts(self) -> List[Post]:
        """전체 게시글 목록 조회 (삭제되지 않은 것만)"""

        return [post for post in self._posts if post.del_yn == "N"]

    def find_by_id(self, post_id: int) -> Optional[Post]:
        """ID로 게시글 조회 (삭제되지 않은 것만)"""
        return next((post for post in self.find_posts() if post.id == post_id), None)

    def create(
        self, title: str, content: str, author_id: int, img_url: Optional[str] = None
    ) -> Post:
        """게시글 생성"""
        post = Post(
            id=self._next_id,
            title=title,
            content=content,
            author_id=author_id,
            img_url=img_url,
        )
        self._posts.append(post)
        self._next_id += 1
        return post

    def update(
        self,
        post_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        img_url: Optional[str] = None,
    ) -> Optional[Post]:
        """게시글 수정"""
        post = self.find_by_id(post_id)
        if not post:
            return None

        if title is not None:
            post.title = title
        if content is not None:
            post.content = content
        if img_url is not None:
            post.img_url = img_url

        return post

    def delete(self, post_id: int) -> bool:
        """게시글 삭제 (논리적 삭제 - del_yn='Y')"""
        post = self.find_by_id(post_id)
        if not post:
            return False

        post.del_yn = "Y"
        return True

    def increase_view_count(self, post_id: int) -> bool:
        """조회수 증가"""
        post = self.find_by_id(post_id)
        if not post:
            return False

        post.view_count += 1
        return True

    def increase_like_count(self, post_id: int) -> bool:
        """좋아요 수 증가"""
        post = self.find_by_id(post_id)
        if not post:
            return False

        post.like_count += 1
        return True

    def decrease_like_count(self, post_id: int) -> bool:
        """좋아요 수 감소 (최소 0)"""
        post = self.find_by_id(post_id)
        if not post:
            return False

        if post.like_count > 0:
            post.like_count -= 1
        return True

    def increase_comment_count(self, post_id: int) -> bool:
        """댓글 수 증가"""
        post = self.find_by_id(post_id)
        if not post:
            return False

        post.comment_count += 1
        return True

    def decrease_comment_count(self, post_id: int) -> bool:
        """댓글 수 감소 (최소 0)"""
        post = self.find_by_id(post_id)
        if not post:
            return False

        if post.comment_count > 0:
            post.comment_count -= 1
        return True

    def get_by_author(self, author_id: int) -> List[Post]:
        """작성자별 게시글 조회 (삭제되지 않은 것만)"""
        return [
            post
            for post in self._posts
            if post.author_id == author_id and post.del_yn == "N"
        ]
