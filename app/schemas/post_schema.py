from typing import Annotated, List, Optional

from pydantic import AfterValidator, BaseModel, Field


def validate_title(value: str) -> str:
    """제목 검증"""
    if not value:
        raise ValueError("제목은 필수 입력 항목입니다.")
    if len(value) < 1 or len(value) > 26:
        raise ValueError("제목은 1자 이상 26자 이하이어야 합니다.")
    return value


def validate_content(value: str) -> str:
    """내용 검증"""
    if not value:
        raise ValueError("내용은 필수 입력 항목입니다.")
    if len(value) < 1 or len(value) > 5000:
        raise ValueError("내용은 1자 이상 5000자 이하이어야 합니다.")
    return value


def validate_comment_content(value: str) -> str:
    """댓글 내용 검증"""
    if not value:
        raise ValueError("댓글 내용은 필수 입력 항목입니다.")
    if len(value) < 1 or len(value) > 1000:
        raise ValueError("댓글 내용은 1자 이상 1000자 이하이어야 합니다.")
    return value


TitleStr = Annotated[str, AfterValidator(validate_title)]
ContentStr = Annotated[str, AfterValidator(validate_content)]
CommentContentStr = Annotated[str, AfterValidator(validate_comment_content)]


class CreatePostRequest(BaseModel):
    """v2 게시글 등록 요청 DTO (JWT 인증)"""

    title: TitleStr = Field(..., description="게시글 제목 (1-26자)")
    content: ContentStr = Field(..., description="게시글 내용 (1-5000자)")
    image_ids: Optional[List[int]] = Field(default=[], description="이미지 ID 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "FastAPI 게시글 제목",
                "content": "FastAPI로 게시판을 만들어봅시다.",
                "image_ids": [1, 2],
            }
        }


class UpdatePostRequest(BaseModel):
    """v2 게시글 수정 요청 DTO (JWT 인증)"""

    title: Optional[TitleStr] = Field(None, description="게시글 제목 (1-26자)")
    content: Optional[ContentStr] = Field(None, description="게시글 내용 (1-5000자)")
    image_ids: Optional[List[int]] = Field(None, description="이미지 ID 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "수정된 제목",
                "content": "수정된 내용입니다.",
                "image_ids": [1, 2],
            }
        }


class PostStatusResponse(BaseModel):
    """게시글 통계 정보 DTO"""

    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0

    class Config:
        json_schema_extra = {
            "example": {"view_count": 42, "like_count": 10, "comment_count": 5}
        }


class CreateCommentRequest(BaseModel):
    """v2 댓글 생성 요청 DTO (JWT 인증)"""

    content: CommentContentStr = Field(..., description="댓글 내용 (1-1000자)")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "유익한 게시글 감사합니다!",
            }
        }


class UpdateCommentRequest(BaseModel):
    """v2 댓글 수정 요청 DTO (JWT 인증)"""

    content: CommentContentStr = Field(..., description="댓글 내용 (1-1000자)")

    class Config:
        json_schema_extra = {"example": {"content": "수정된 댓글 내용입니다."}}


class CommentAuthor(BaseModel):
    """댓글 작성자 정보 DTO"""

    id: int
    nick_name: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 2,
                "nick_name": "홍길동",
                "image_url": "https://example.com/profile.jpg",
            }
        }


class CommentResponse(BaseModel):
    """댓글 응답 DTO"""

    id: int
    post_id: int
    author: CommentAuthor
    content: str
    created_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "post_id": 1,
                "author": {
                    "id": 2,
                    "nick_name": "홍길동",
                    "image_url": "https://example.com/profile.jpg",
                },
                "content": "유익한 게시글 감사합니다!",
                "created_at": "2025-11-13 21:00:00",
            }
        }


class CommentCursorInfo(BaseModel):
    """댓글 커서 페이지네이션 정보 DTO"""

    comments: List[CommentResponse]
    next_cursor: Optional[int] = None
    has_next: bool = False
    total: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "comments": [
                    {
                        "id": 10,
                        "post_id": 1,
                        "author": {
                            "id": 2,
                            "nick_name": "홍길동",
                            "image_url": "https://example.com/profile.jpg",
                        },
                        "content": "댓글 내용",
                        "created_at": "2025-11-13 21:00:00",
                    }
                ],
                "next_cursor": 9,
                "has_next": True,
                "total": 15,
            }
        }


class PostResponse(BaseModel):
    """게시글 응답 DTO (상세 조회용)"""

    id: int
    title: str
    content: str
    author_id: int
    img_url: Optional[str] = None
    status: PostStatusResponse
    del_yn: str
    created_at: str
    comments: CommentCursorInfo = CommentCursorInfo(comments=[], next_cursor=None, has_next=False, total=0)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "FastAPI 게시글 제목",
                "content": "FastAPI로 게시판을 만들어봅시다.",
                "author_id": 1,
                "img_url": "https://example.com/image.jpg",
                "status": {"view_count": 42, "like_count": 10, "comment_count": 5},
                "del_yn": "N",
                "created_at": "2025-01-13 10:30:00",
                "comments": {
                    "comments": [
                        {
                            "id": 1,
                            "post_id": 1,
                            "author": {
                                "id": 2,
                                "nick_name": "홍길동",
                                "image_url": "https://example.com/profile.jpg",
                            },
                            "content": "첫 번째 댓글입니다.",
                            "created_at": "2025-11-13 21:00:00",
                        }
                    ],
                    "next_cursor": None,
                    "has_next": False,
                    "total": 1,
                },
            }
        }


class PostListResponse(BaseModel):
    """게시글 목록 응답 DTO"""

    posts: List[PostResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "posts": [
                    {
                        "id": 1,
                        "title": "첫 번째 게시글",
                        "content": "내용...",
                        "author_id": 1,
                        "img_url": None,
                        "status": {
                            "view_count": 10,
                            "like_count": 2,
                            "comment_count": 0,
                        },
                        "del_yn": "N",
                        "created_at": "2025-01-13 10:30:00",
                        "comments": [],
                    }
                ],
                "total": 1,
            }
        }


class PostCursorResponse(BaseModel):
    """게시글 목록 커서 페이지네이션 응답 DTO"""

    posts: List[PostResponse]
    next_cursor: Optional[int] = None
    has_next: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "posts": [
                    {
                        "id": 10,
                        "title": "게시글 제목",
                        "content": "게시글 내용...",
                        "author_id": 1,
                        "img_url": None,
                        "status": {
                            "view_count": 10,
                            "like_count": 2,
                            "comment_count": 5,
                        },
                        "del_yn": "N",
                        "created_at": "2025-11-13 10:30:00",
                        "comments": [],
                    }
                ],
                "next_cursor": 9,
                "has_next": True,
            }
        }
