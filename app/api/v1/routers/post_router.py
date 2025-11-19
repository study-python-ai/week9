from fastapi import APIRouter, Depends, status
from app.api.v1.controllers.post_controller import PostController
from app.models.post_model import PostModel
from app.models.user_model import UserModel
from app.models.comment_model import CommentModel
from app.dependencies import get_post_model, get_user_model, get_comment_model
from app.schemas.v1 import (
    CreatePostRequest,
    UpdatePostRequest,
    PostResponse,
    PostListResponse,
    CreateCommentRequest,
    UpdateCommentRequest,
)

router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


def get_post_controller(
    post_model: PostModel = Depends(get_post_model),
    user_model: UserModel = Depends(get_user_model),
    comment_model: CommentModel = Depends(get_comment_model),
) -> PostController:
    """게시글 컨트롤러 의존성 주입

    Args:
        post_model: 게시글 모델 (의존성 주입)
        user_model: 사용자 모델 (의존성 주입)
        comment_model: 댓글 모델 (의존성 주입)

    Returns:
        PostController: 게시글 컨트롤러 인스턴스
    """
    return PostController(post_model, user_model, comment_model)


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: CreatePostRequest,
    controller: PostController = Depends(get_post_controller),
):
    """게시글 등록

    Args:

        request: 게시글 등록 요청
            - title: 게시글 제목 (1-100자)
            - content: 게시글 내용 (1-5000자)
            - author_id: 작성자 ID
            - img_url: 이미지 URL (선택)
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:

        PostResponse: 생성된 게시글

    Raises:

        NotFoundException: 작성자가 존재하지 않는 경우
    """
    return controller.create_post(request)


@router.get("", response_model=PostListResponse, status_code=status.HTTP_200_OK)
async def get_posts(controller: PostController = Depends(get_post_controller)):
    """게시글 목록 조회

    삭제되지 않은 모든 게시글을 조회합니다.

    Args:

        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:
        PostListResponse: 게시글 목록 및 총 개수
    """
    return controller.get_posts()


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def get_post(
    post_id: int, controller: PostController = Depends(get_post_controller)
):
    """게시글 상세 조회

    게시글을 조회하고 조회수를 1 증가시킵니다.

    Args:

        post_id: 게시글 ID
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:

        PostResponse: 게시글

    Raises:

        NotFoundException: 게시글을 찾을 수 없는 경우
    """
    return controller.get_post(post_id)


@router.patch("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def update_post(
    post_id: int,
    request: UpdatePostRequest,
    controller: PostController = Depends(get_post_controller),
):
    """게시글 수정

    작성자만 게시글을 수정할 수 있습니다.

    Args:

        post_id: 게시글 ID
        request: 게시글 수정 요청
            - title: 게시글 제목 (선택)
            - content: 게시글 내용 (선택)
            - img_url: 이미지 URL (선택)
            - author_id: 요청자 ID (권한 검증용)
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:

        PostResponse: 수정된 게시글

    Raises:

        NotFoundException: 게시글을 찾을 수 없는 경우
        UnauthorizedException: 작성자가 아닌 경우
    """
    return controller.update_post(post_id, request)


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
    post_id: int,
    author_id: int,
    controller: PostController = Depends(get_post_controller),
):
    """게시글 삭제

    작성자만 게시글을 삭제할 수 있습니다.

    Args:

        post_id: 게시글 ID
        author_id: 요청자 ID (권한 검증용, 쿼리 파라미터)
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:

        dict: 성공 메시지

    Raises:

        NotFoundException: 게시글을 찾을 수 없는 경우
        UnauthorizedException: 작성자가 아닌 경우
    """
    return controller.delete_post(post_id, author_id)


@router.post(
    "/{post_id}/like", response_model=PostResponse, status_code=status.HTTP_200_OK
)
async def like_post(
    post_id: int, controller: PostController = Depends(get_post_controller)
):
    """게시글 좋아요

    게시글의 좋아요 수를 1 증가합니다.

    Args:

        post_id: 게시글 ID
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:

        PostResponse: 좋아요 수가 증가한 게시글

    Raises:

        NotFoundException: 게시글을 찾을 수 없는 경우
    """
    return controller.like_post(post_id)


@router.delete(
    "/{post_id}/like", response_model=PostResponse, status_code=status.HTTP_200_OK
)
async def unlike_post(
    post_id: int, controller: PostController = Depends(get_post_controller)
):
    """게시글 좋아요 취소

    게시글의 좋아요 수를 감소 합니다.

    Args:

        post_id: 게시글 ID
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:

        PostResponse: 좋아요 수가 감소된 게시글

    Raises:

        NotFoundException: 게시글을 찾을 수 없는 경우
    """
    return controller.unlike_post(post_id)


@router.post(
    "/{post_id}/comment",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    post_id: int,
    request: CreateCommentRequest,
    controller: PostController = Depends(get_post_controller),
):
    """댓글 생성

    게시글에 새로운 댓글을 추가합니다.

    Args:

        post_id: 게시글 ID
        request: 댓글 생성 요청
            - content: 댓글 내용 (1-1000자)
            - author_id: 작성자 ID
            - img_url: 프로필 이미지 URL (선택)
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:

        PostResponse: 댓글이 추가된 게시글

    Raises:

        NotFoundException: 게시글 또는 작성자를 찾을 수 없는 경우
    """
    return controller.add_comment(post_id, request)


@router.patch(
    "/{post_id}/comment/{comment_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
)
async def update_comment(
    post_id: int,
    comment_id: int,
    request: UpdateCommentRequest,
    controller: PostController = Depends(get_post_controller),
):
    """댓글 수정

    작성자만 댓글을 수정할 수 있습니다.

    Args:

        post_id: 게시글 ID
        comment_id: 댓글 ID
        request: 댓글 수정 요청
            - content: 댓글 내용 (1-1000자)
            - author_id: 요청자 ID (권한 검증용)
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:

        PostResponse: 댓글이 수정된 게시글

    Raises:

        NotFoundException: 게시글 또는 댓글을 찾을 수 없는 경우
        UnauthorizedException: 작성자가 아닌 경우
    """
    return controller.update_comment(post_id, comment_id, request)


@router.delete(
    "/{post_id}/comment/{comment_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
)
async def remove_comment(
    post_id: int,
    comment_id: int,
    author_id: int,
    controller: PostController = Depends(get_post_controller),
):
    """댓글 삭제

    작성자만 댓글을 삭제할 수 있습니다.

    Args:

        post_id: 게시글 ID
        comment_id: 댓글 ID
        author_id: 요청자 ID (권한 검증용, 쿼리 파라미터)
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:

        PostResponse: 댓글이 삭제된 게시글

    Raises:

        NotFoundException: 게시글 또는 댓글을 찾을 수 없는 경우
        UnauthorizedException: 작성자가 아닌 경우
    """
    return controller.remove_comment(post_id, comment_id, author_id)
