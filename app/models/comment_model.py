from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class DeleteStatus(str, Enum):
    """삭제 상태"""

    NOT_DELETED = "N"
    DELETED = "Y"


@dataclass
class Comment:
    """댓글 모델"""

    id: int = field(init=False)
    post_id: int
    author_id: int
    content: str
    img_url: Optional[str] = None
    del_yn: str = DeleteStatus.NOT_DELETED.value
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def delete(self) -> None:
        """댓글 논리적 삭제"""
        self.del_yn = DeleteStatus.DELETED.value


@dataclass
class Comments:
    """댓글 컬렉션"""

    def __init__(self, comments: List[Comment], condition=None):
        self._comments = comments
        self.condition = condition

    def __iter__(self):
        return iter(self._comments)

    def __len__(self):
        return len(self._comments)

    def __getitem__(self, index):
        return self._comments[index]

    def __add__(self, other):
        return Comments(self._comments + other._comments)

    def append(self, comment: Comment, next_id: int) -> None:
        """댓글 추가

        Args:
            comment: 추가할 댓글
            next_id: 할당할 ID
        """
        comment.id = next_id
        self._comments.append(comment)

    def get(self, condition) -> 'Comments':
        """조건에 맞는 댓글만 필터링"""
        comments: List[Comment] = [
            comment for comment in self._comments if condition(comment)
        ]
        return Comments(comments, condition=condition)

    def get_condition_not_delete(self, condition) -> 'Comments':
        """삭제되지 않은 댓글만 필터링"""
        return self.get(
            lambda comment: comment.del_yn == DeleteStatus.NOT_DELETED.value
            and condition(comment)
        )

    def get_comment(self, comment_id: int) -> Optional[Comment]:
        """댓글 단건 조회"""
        comments = self.get_condition_not_delete(lambda comment: comment.id == comment_id)
        return comments._comments[0] if len(comments) > 0 else None

    def to_list(self) -> List[Comment]:
        """댓글 리스트 반환"""
        return self._comments


class CommentModel:
    """댓글 데이터 관리"""

    def __init__(self):
        self._comments: Comments = Comments([])
        self._next_id: int = 1

    def create(
        self, post_id: int, author_id: int, content: str, img_url: Optional[str] = None
    ) -> Comment:
        """댓글 생성

        Args:
            post_id: 게시글 ID
            author_id: 작성자 ID
            content: 댓글 내용
            img_url: 이미지 URL (선택)

        Returns:
            Comment: 생성된 댓글
        """
        comment = Comment(
            post_id=post_id, author_id=author_id, content=content, img_url=img_url
        )

        self._comments.append(comment, self._next_id)
        self._next_id += 1
        return comment

    def find_by_id(self, comment_id: int) -> Optional[Comment]:
        """ID로 댓글 조회

        Args:
            comment_id: 댓글 ID

        Returns:
            Optional[Comment]: 댓글 (없으면 None)
        """
        return self._comments.get_comment(comment_id)

    def find_by_post_id(self, post_id: int) -> List[Comment]:
        """게시글의 모든 댓글 조회

        Args:
            post_id: 게시글 ID

        Returns:
            List[Comment]: 댓글 목록
        """
        comments = self._comments.get_condition_not_delete(
            lambda comment: comment.post_id == post_id
        )
        return comments.to_list()

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
        return len(self.find_by_post_id(post_id))

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
        return comment
