from functools import lru_cache
from app.models.user_model import UserModel
from app.models.post_model import PostModel
from app.models.comment_model import CommentModel
from app.models.like_model import LikeModel


@lru_cache()
def get_user_model() -> UserModel:
    """사용자 모델 의존성

    @lru_cache 데코레이터를 사용하여 싱글톤 인스턴스 반환

    Returns:
        UserModel: 사용자 모델 인스턴스
    """
    return UserModel()


@lru_cache()
def get_post_model() -> PostModel:
    """게시글 모델 의존성

    @lru_cache 데코레이터를 사용하여 싱글톤 인스턴스 반환

    Returns:
        PostModel: 게시글 모델 인스턴스
    """
    return PostModel()


@lru_cache()
def get_comment_model() -> CommentModel:
    """댓글 모델 의존성

    @lru_cache 데코레이터를 사용하여 싱글톤 인스턴스 반환

    Returns:
        CommentModel: 댓글 모델 인스턴스
    """
    return CommentModel()


@lru_cache()
def get_like_model() -> LikeModel:
    """좋아요 모델 의존성

    @lru_cache 데코레이터를 사용하여 싱글톤 인스턴스 반환

    Returns:
        LikeModel: 좋아요 모델 인스턴스
    """
    return LikeModel()
