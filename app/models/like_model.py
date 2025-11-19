from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Like:
    """좋아요"""

    post_id: int
    user_id: int
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Likes:
    """좋아요 컬렉션"""

    def __init__(self):
        self._likes: List[Like] = []

    def add(self, post_id: int, user_id: int) -> Like:
        """좋아요 추가"""
        like = Like(post_id=post_id, user_id=user_id)
        self._likes.append(like)
        return like

    def remove(self, post_id: int, user_id: int) -> bool:
        """좋아요 제거"""
        for i, like in enumerate(self._likes):
            if like.post_id == post_id and like.user_id == user_id:
                self._likes.pop(i)
                return True
        return False

    def exists(self, post_id: int, user_id: int) -> bool:
        """좋아요 존재 여부 확인"""
        return any(
            like.post_id == post_id and like.user_id == user_id
            for like in self._likes
        )

    def get_by_post_id(self, post_id: int) -> List[Like]:
        """게시글의 모든 좋아요 조회"""
        return [like for like in self._likes if like.post_id == post_id]

    def get_by_user_id(self, user_id: int) -> List[Like]:
        """사용자의 모든 좋아요 조회"""
        return [like for like in self._likes if like.user_id == user_id]


class LikeModel:
    """좋아요 모델"""

    def __init__(self):
        self._likes = Likes()

    def add_like(self, post_id: int, user_id: int) -> Optional[Like]:
        """좋아요 추가

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID

        Returns:
            Optional[Like]: 추가된 좋아요 (이미 존재하면 None)
        """
        if self._likes.exists(post_id, user_id):
            return None
        return self._likes.add(post_id, user_id)

    def remove_like(self, post_id: int, user_id: int) -> bool:
        """좋아요 제거

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID

        Returns:
            bool: 제거 성공 여부
        """
        return self._likes.remove(post_id, user_id)

    def has_liked(self, post_id: int, user_id: int) -> bool:
        """좋아요 여부 확인

        Args:
            post_id: 게시글 ID
            user_id: 사용자 ID

        Returns:
            bool: 좋아요 여부
        """
        return self._likes.exists(post_id, user_id)

    def get_likes_by_post(self, post_id: int) -> List[Like]:
        """게시글의 좋아요 목록 조회

        Args:
            post_id: 게시글 ID

        Returns:
            List[Like]: 좋아요 목록
        """
        return self._likes.get_by_post_id(post_id)
