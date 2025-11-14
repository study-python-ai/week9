from typing import Annotated, Optional, List
from pydantic import BaseModel, AfterValidator, Field


def validate_title(value: str) -> str:
    """제목 검증"""
    if not value:
        raise ValueError("제목은 필수 입력 항목입니다.")
    if len(value) < 1 or len(value) > 100:
        raise ValueError("제목은 1자 이상 100자 이하이어야 합니다.")
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
    """게시글 등록 요청 DTO"""
    title: TitleStr = Field(..., description="게시글 제목 (1-100자)")
    content: ContentStr = Field(..., description="게시글 내용 (1-5000자)")
    author_id: int = Field(..., gt=0, description="작성자 ID")
    img_url: Optional[str] = Field(None, description="이미지 URL")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "FastAPI 게시글 제목",
                "content": "FastAPI로 게시판을 만들어봅시다.",
                "author_id": 1,
                "img_url": "https://example.com/image.jpg"
            }
        }


class UpdatePostRequest(BaseModel):
    """게시글 수정 요청 DTO"""
    title: Optional[TitleStr] = Field(None, description="게시글 제목 (1-100자)")
    content: Optional[ContentStr] = Field(None, description="게시글 내용 (1-5000자)")
    img_url: Optional[str] = Field(None, description="이미지 URL")
    author_id: int = Field(..., gt=0, description="요청자 ID (권한 검증용)")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "수정된 제목",
                "content": "수정된 내용입니다.",
                "img_url": "https://example.com/new-image.jpg",
                "author_id": 1
            }
        }


class PostStatusResponse(BaseModel):
    """게시글 통계 정보 DTO"""
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "view_count": 42,
                "like_count": 10,
                "comment_count": 5
            }
        }


class CreateCommentRequest(BaseModel):
    """댓글 생성 요청 DTO"""
    content: CommentContentStr = Field(..., description="댓글 내용 (1-1000자)")
    author_id: int = Field(..., gt=0, description="작성자 ID")
    img_url: Optional[str] = Field(None, description="프로필 이미지 URL")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "유익한 게시글 감사합니다!",
                "author_id": 2,
                "img_url": "https://example.com/profile.jpg"
            }
        }


class UpdateCommentRequest(BaseModel):
    """댓글 수정 요청 DTO"""
    content: CommentContentStr = Field(..., description="댓글 내용 (1-1000자)")
    author_id: int = Field(..., gt=0, description="요청자 ID (권한 검증용)")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "수정된 댓글 내용입니다.",
                "author_id": 2
            }
        }


class CommentResponse(BaseModel):
    """댓글 응답 DTO"""
    id: int
    post_id: int
    author_id: int
    content: str
    img_url: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "post_id": 1,
                "author_id": 2,
                "content": "유익한 게시글 감사합니다!",
                "img_url": "https://example.com/profile.jpg",
                "created_at": "2025-11-13T21:00:00"
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
    comments: List[CommentResponse] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "FastAPI 게시글 제목",
                "content": "FastAPI로 게시판을 만들어봅시다.",
                "author_id": 1,
                "img_url": "https://example.com/image.jpg",
                "status": {
                    "view_count": 42,
                    "like_count": 10,
                    "comment_count": 5
                },
                "del_yn": "N",
                "created_at": "2025-01-13T10:30:00",
                "comments": [
                    {
                        "id": 1,
                        "img_url": "https://example.com/profile.jpg",
                        "content": "첫 번째 댓글입니다."
                    }
                ]
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
                            "comment_count": 0
                        },
                        "del_yn": "N",
                        "created_at": "2025-01-13T10:30:00",
                        "comments": []
                    }
                ],
                "total": 1
            }
        }
