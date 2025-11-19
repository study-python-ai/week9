from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class DeleteStatus(str, Enum):
    """삭제 상태"""

    NOT_DELETED = "N"
    DELETED = "Y"


@dataclass
class PostStatus:
    """게시글 상태 모델"""

    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0

    def increase_view_count(self) -> None:
        """조회수 증가"""
        self.view_count += 1

    def increase_like_count(self) -> None:
        """좋아요 수 증가"""
        self.like_count += 1

    def decrease_like_count(self) -> None:
        """좋아요 수 감소"""
        if self.like_count > 0:
            self.like_count -= 1

    # @FIXME DB 연결시 삭제
    def increase_comment_count(self) -> None:
        """댓글 수 증가"""
        self.comment_count += 1

    # @FIXME DB 연결시 삭제
    def decrease_comment_count(self) -> None:
        """댓글 수 감소"""
        if self.comment_count > 0:
            self.comment_count -= 1


@dataclass
class Post:
    """게시글 모델"""

    id: int = field(init=False)
    author_id: int
    title: str
    content: str
    img_url: Optional[str] = None
    status: PostStatus = field(
        default_factory=lambda: PostStatus(view_count=0, like_count=0, comment_count=0)
    )
    del_yn: str = DeleteStatus.NOT_DELETED
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def _change_title(self, title: str) -> None:
        """제목 변경"""
        self.title = title

    def _change_content(self, content: str) -> None:
        """내용 변경"""
        self.content = content

    def _change_img_url(self, img_url: str) -> None:
        """이미지 URL 변경"""
        self.img_url = img_url

    def delete(self) -> None:
        """게시글 논리적 삭제"""
        self.del_yn = DeleteStatus.DELETED

    def increase_view_count(self) -> None:
        """조회수 증가"""
        self.status.increase_view_count()

    def increase_like_count(self) -> None:
        """좋아요 수 증가"""
        self.status.increase_like_count()

    def decrease_like_count(self) -> None:
        """좋아요 수 감소"""
        self.status.decrease_like_count()

    def increase_comment_count(self) -> None:
        """댓글 수 증가"""
        self.status.increase_comment_count()

    def decrease_comment_count(self) -> None:
        """댓글 수 감소"""
        self.status.decrease_comment_count()

    def change_post(
        self, title: Optional[str], content: Optional[str], img_url: Optional[str]
    ) -> 'Post':
        """게시글 정보 변경"""
        if title is not None:
            self._change_title(title)

        if content is not None:
            self._change_content(content)

        if img_url is not None:
            self._change_img_url(img_url)

        self.updated_at = datetime.now().isoformat()
        return self


@dataclass
class Posts:
    """게시글"""

    def __init__(self, posts: List[Post], condition=None):
        self._posts = posts
        self.condition = condition

    def __iter__(self):
        return iter(self._posts)

    def __len__(self):
        return len(self._posts)

    def __getitem__(self, index):
        return self._posts[index]

    def __add__(self, other):
        return Posts(self._posts + other._posts)

    def append(self, post: Post, next_id: int) -> None:
        """게시글 추가

        Args:
            post: 추가할 게시글
            next_id: 할당할 ID
        """
        post.id = next_id
        self._posts.append(post)

    def get(self, condition) -> 'Posts':
        """조건에 맞는 게시글만 필터링

        Args:
            condition: 필터링 조건 함수

        Returns:
            Posts: 조건에 맞는 게시글 컬렉션
        """

        posts: List[Post] = [post for post in self._posts if condition(post)]
        return Posts(posts, condition=condition)

    def get_condition_not_delete(self, condition) -> 'Posts':
        """삭제되지 않은 게시글만 필터링"""
        return self.get(
            lambda post: post.del_yn == DeleteStatus.NOT_DELETED and condition(post)
        )

    def get_post(self, id: int) -> Optional[Post]:
        """게시글 단건 조회

        Args:
            id: 게시글 ID
        Returns:
            Post: 게시글
        """

        posts = self.get_condition_not_delete(lambda post: post.id == id)
        return posts._posts[0] if len(posts) > 0 else None

    def to_list(self) -> List[Post]:
        """게시글 리스트 반환"""
        return self._posts


class PostModel:
    """게시글 모델 관리 (인메모리)"""

    def __init__(self):
        self._posts: Posts = Posts([])
        self._next_id: int = 1

    def find_posts(self, cursor_id: Optional[int] = None, limit: int = 10) -> Posts:
        """전체 게시글 목록 조회

        Args:
            cursor_id (int, optional): 커서 ID. 페이지 네비게이션에 사용
            limit (int, optional): 조회할 게시글 수.

        Returns:
            Posts: 게시글 목록
        """

        # 커서 ID가 주어진 경우 해당 ID보다 작은 게시글부터 조회
        if cursor_id is not None:
            return self._posts.get_condition_not_delete(
                lambda post: post.id < cursor_id
            )[:limit]
        else:
            # 커서 ID가 없는 경우 최신 게시글부터 조회
            return self._posts.get_condition_not_delete(lambda post: True)[:limit]

    def find_by_id(self, post_id: int) -> Optional[Post]:
        """게시글 단건 조회

        Args:
            post_id (int): 게시글 ID

        Returns:
            Post: 게시글
        """

        return self._posts.get_post(post_id)

    def create(
        self, title: str, content: str, author_id: int, img_url: Optional[str] = None
    ) -> Post:
        """게시글 생성"""

        # 게시글 생성
        post = Post(author_id=author_id, title=title, content=content, img_url=img_url)

        # 게시글 컬렉션에 저장
        self._posts.append(post, self._next_id)
        self._next_id += 1

        return post

    def update(
        self,
        id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        img_url: Optional[str] = None,
    ) -> Optional[Post]:
        """게시글 수정"""
        post = self.find_by_id(id)

        # 게시글 필수 항목이 모두 비어있는 경우 None 반환
        if not post:
            return None

        post.change_post(title, content, img_url)

        return post

    def delete(self, id: int) -> bool:
        """게시글 삭제 (논리적 삭제 - del_yn='Y')"""
        post = self.find_by_id(id)

        if not post:
            return False

        post.delete()
        return True

    def increase_view_count(self, post_id: int) -> bool:
        """조회수 증가"""
        post = self.find_by_id(post_id)
        if not post:
            return False

        post.increase_view_count()
        return True

    def increase_like_count(self, post_id: int) -> bool:
        """좋아요 수 증가"""
        post = self.find_by_id(post_id)

        if not post:
            return False

        post.increase_like_count()
        return True

    def decrease_like_count(self, post_id: int) -> bool:
        """좋아요 수 감소"""
        post = self.find_by_id(post_id)

        if not post:
            return False

        post.decrease_like_count()
        return True

    def increase_comment_count(self, post_id: int) -> bool:
        """댓글 수 증가"""
        post = self.find_by_id(post_id)

        if not post:
            return False

        post.increase_comment_count()
        return True

    def decrease_comment_count(self, post_id: int) -> bool:
        """댓글 수 감소"""
        post = self.find_by_id(post_id)

        if not post:
            return False

        post.decrease_comment_count()
        return True
