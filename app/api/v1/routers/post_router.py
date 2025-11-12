from fastapi import APIRouter, Depends, status
from app.api.v1.controllers.post_controller import PostController
from app.schemas.post_schema import (
    CreatePostRequest,
    UpdatePostRequest,
    PostResponse,
    PostListResponse
)

router = APIRouter(prefix="/api/v1/posts", tags=["posts"])


def get_post_controller() -> PostController:
    """의존성 주입을 위한 컨트롤러 팩토리

    Returns:
        PostController: 게시글 컨트롤러 인스턴스
    """
    return PostController()


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    request: CreatePostRequest,
    controller: PostController = Depends(get_post_controller)
):
    """게시글 등록

    Args:
        request: 게시글 등록 요청 정보
            - title: 게시글 제목 (1-100자)
            - content: 게시글 내용 (1-5000자)
            - author_id: 작성자 ID
            - img_url: 이미지 URL (선택)
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:
        PostResponse: 생성된 게시글 정보

    Raises:
        NotFoundException: 작성자가 존재하지 않는 경우
    """
    return controller.create_post(request)


@router.get("", response_model=PostListResponse, status_code=status.HTTP_200_OK)
async def get_posts(
    controller: PostController = Depends(get_post_controller)
):
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
    post_id: int,
    controller: PostController = Depends(get_post_controller)
):
    """게시글 상세 조회

    게시글을 조회하고 조회수를 1 증가시킵니다.

    Args:
        post_id: 게시글 ID
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:
        PostResponse: 게시글 정보

    Raises:
        NotFoundException: 게시글을 찾을 수 없는 경우
    """
    return controller.get_post(post_id)


@router.patch("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def update_post(
    post_id: int,
    request: UpdatePostRequest,
    controller: PostController = Depends(get_post_controller)
):
    """게시글 수정

    작성자만 게시글을 수정할 수 있습니다.

    Args:
        post_id: 게시글 ID
        request: 게시글 수정 요청 정보
            - title: 게시글 제목 (선택)
            - content: 게시글 내용 (선택)
            - img_url: 이미지 URL (선택)
            - author_id: 요청자 ID (권한 검증용)
        controller: 게시글 컨트롤러 (의존성 주입)

    Returns:
        PostResponse: 수정된 게시글 정보

    Raises:
        NotFoundException: 게시글을 찾을 수 없는 경우
        UnauthorizedException: 작성자가 아닌 경우
    """
    return controller.update_post(post_id, request)


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
    post_id: int,
    author_id: int,
    controller: PostController = Depends(get_post_controller)
):
    """게시글 삭제

    작성자만 게시글을 삭제할 수 있습니다.
    논리적 삭제(del_yn='Y')가 수행됩니다.

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
