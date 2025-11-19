from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v2.controllers.post_controller import PostController
from app.core.db.dependencies import get_db, get_post_model, get_user_model
from app.core.security.dependencies import get_current_user, get_optional_current_user
from app.models.user_model import User
from app.schemas import (
    CreateCommentRequest,
    CreatePostRequest,
    PostListResponse,
    PostResponse,
    UpdateCommentRequest,
    UpdatePostRequest,
)

router = APIRouter(prefix="/api/v2/posts", tags=["v2-posts"])


def get_post_controller(db: Session = Depends(get_db)) -> PostController:
    """
    PostController 의존성 주입 함수

    Aggregate 패턴을 적용하여 PostController 인스턴스를 생성

    Args:
        db: 데이터베이스 세션

    Returns:
        PostController: 게시글 컨트롤러 인스턴스
    """
    return PostController(get_post_model(db), get_user_model(db))


@router.get("", response_model=PostListResponse)
def get_posts(controller: PostController = Depends(get_post_controller)):
    """
    게시글 목록 조회

    모든 게시글 목록을 조회

    Args:
        controller: 게시글 컨트롤러

    Returns:
        PostListResponse: 게시글 목록 응답
    """
    return controller.get_posts()


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    request: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """
    게시글 생성

    인증된 사용자만 게시글을 작성

    Args:
        request: 게시글 생성 요청 데이터
        current_user: 현재 인증된 사용자
        controller: 게시글 컨트롤러

    Returns:
        PostResponse: 생성된 게시글 응답

    Raises:
        HTTPException: 인증되지 않은 경우 401 에러
    """
    return controller.create_post(request, current_user)


@router.get("/{id}", response_model=PostResponse)
def get_post(
    id: int,
    current_user: Optional[User] = Depends(get_optional_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """
    게시글 상세 조회

    사용자 로그인시 조회수 증가
    사용자 비로그인시 조회수 증가하지 않음

    Args:
        id: 조회할 게시글 ID
        current_user: 현재 인증된 사용자
        controller: 게시글 컨트롤러

    Returns:
        PostResponse: 게시글 상세 응답

    Raises:
        HTTPException: 게시글을 찾을 수 없는 경우 404 에러
    """
    return controller.get_post(id, current_user)


@router.patch("/{id}", response_model=PostResponse)
def update_post(
    id: int,
    request: UpdatePostRequest,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """
    게시글 수정

    게시글 작성자만 자신의 게시글을 수정

    Args:
        id: 수정할 게시글 ID
        request: 게시글 수정 요청 데이터
        current_user: 현재 인증된 사용자
        controller: 게시글 컨트롤러

    Returns:
        PostResponse: 수정된 게시글 응답

    Raises:
        HTTPException: 게시글을 찾을 수 없는 경우 404 에러
        HTTPException: 권한이 없는 경우 403 에러
    """
    return controller.update_post(id, request, current_user)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """
    게시글 삭제

    게시글 작성자만 자신의 게시글을 삭제

    Args:
        id: 삭제할 게시글 ID
        current_user: 현재 인증된 사용자
        controller: 게시글 컨트롤러

    Returns:
        None: 204 No Content 응답

    Raises:
        HTTPException: 게시글을 찾을 수 없는 경우 404 에러
        HTTPException: 권한이 없는 경우 403 에러
    """
    controller.delete_post(id, current_user)


@router.post(
    "/{id}/like", response_model=PostResponse, status_code=status.HTTP_201_CREATED
)
def like_post(
    id: int,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """게시글 좋아요"""
    return controller.like_post(id, current_user)


@router.delete("/{id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
    id: int,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """게시글 좋아요 취소"""
    controller.unlike_post(id, current_user)


@router.post(
    "/{id}/comments", response_model=PostResponse, status_code=status.HTTP_201_CREATED
)
def add_comment(
    id: int,
    request: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """댓글 생성"""
    return controller.add_comment(id, request, current_user)


@router.patch("/{post_id}/comments/{id}", response_model=PostResponse)
def update_comment(
    post_id: int,
    id: int,
    request: UpdateCommentRequest,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """댓글 수정"""
    return controller.update_comment(post_id, id, request, current_user)


@router.delete("/{post_id}/comments/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_comment(
    post_id: int,
    id: int,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """댓글 삭제"""
    controller.remove_comment(post_id, id, current_user)
