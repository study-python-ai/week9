from fastapi import APIRouter, Depends, status

from app.api.v2.controllers.post_controller import PostController
from app.common.dependencies import get_current_user
from app.dependencies import get_comment_model, get_like_model, get_post_model, get_user_model
from app.models.comment_model import CommentModel
from app.models.like_model import LikeModel
from app.models.post_model import PostModel
from app.models.user_model import User, UserModel
from app.schemas.v2 import (
    CreateCommentRequest,
    CreatePostRequest,
    PostListResponse,
    PostResponse,
    UpdateCommentRequest,
    UpdatePostRequest,
)

router = APIRouter(prefix="/api/v2/posts", tags=["v2-posts"])


def get_post_controller(
    post_model: PostModel = Depends(get_post_model),
    user_model: UserModel = Depends(get_user_model),
    comment_model: CommentModel = Depends(get_comment_model),
    like_model: LikeModel = Depends(get_like_model),
) -> PostController:
    return PostController(post_model, user_model, comment_model, like_model)


@router.get("", response_model=PostListResponse)
def get_posts(controller: PostController = Depends(get_post_controller)):
    """게시글 목록 조회"""
    return controller.get_posts()


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    request: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """게시글 생성 (인증 필요)"""
    return controller.create_post(request, current_user)


@router.get("/{id}", response_model=PostResponse)
def get_post(id: int, controller: PostController = Depends(get_post_controller)):
    """게시글 상세 조회"""
    return controller.get_post(id)


@router.patch("/{id}", response_model=PostResponse)
def update_post(
    id: int,
    request: UpdatePostRequest,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """게시글 수정"""
    return controller.update_post(id, request, current_user)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    current_user: User = Depends(get_current_user),
    controller: PostController = Depends(get_post_controller),
):
    """게시글 삭제"""
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
