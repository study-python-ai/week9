from typing import Generator
from sqlalchemy.orm import Session
from app.models.user_model import UserModel
from app.models.post_model import PostModel
from app.models.comment_model import CommentModel
from app.models.like_model import LikeModel
from app.models.view_model import ViewModel
from app.core.db.database import SessionLocal


def get_user_model(db: Session) -> UserModel:
    """사용자 모델 의존성

    Args:
        db: 데이터베이스 세션

    Returns:
        UserModel: 사용자 모델 인스턴스
    """
    return UserModel(db)


def get_post_model(db: Session) -> PostModel:
    """게시글 모델 의존성

    Args:
        db: 데이터베이스 세션

    Returns:
        PostModel: 게시글 모델 인스턴스
    """
    return PostModel(db)


def get_comment_model(db: Session) -> CommentModel:
    """댓글 모델 의존성

    Args:
        db: 데이터베이스 세션

    Returns:
        CommentModel: 댓글 모델 인스턴스
    """
    return CommentModel(db)


def get_like_model(db: Session) -> LikeModel:
    """좋아요 모델 의존성

    Args:
        db: 데이터베이스 세션

    Returns:
        LikeModel: 좋아요 모델 인스턴스
    """
    return LikeModel(db)


def get_view_model(db: Session) -> ViewModel:
    """조회 모델 의존성

    Args:
        db: 데이터베이스 세션

    Returns:
        ViewModel: 조회 모델 인스턴스
    """
    return ViewModel(db)


def get_db() -> Generator[Session, None, None]:
    """데이터베이스 세션 의존성

    SQLAlchemy 세션을 생성하고 요청 처리 후 자동으로 닫습니다.

    Yields:
        Session: SQLAlchemy 데이터베이스 세션
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
