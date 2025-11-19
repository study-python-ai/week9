from typing import Optional

from app.core.exceptions.error_codes import ErrorCode
from app.core.exceptions.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
)
from app.core.validators import get_or_raise
from app.models.post_model import Post, PostModel
from app.models.user_model import User, UserModel
from app.schemas import (
    CommentResponse,
    CreateCommentRequest,
    CreatePostRequest,
    PostListResponse,
    PostResponse,
    PostStatusResponse,
    UpdateCommentRequest,
    UpdatePostRequest,
)


class PostController:
    """v2 게시글 컨트롤러 (Aggregate 패턴 적용)"""

    def __init__(self, post_model: PostModel, user_model: UserModel):
        self.post_model = post_model
        self.user_model = user_model

    def _convert_to_response(self, post: Post) -> PostResponse:
        """Post 객체를 PostResponse로 변환 (Aggregate 패턴)"""
        comments = self.post_model.get_comments(post.id)
        comment_responses = [
            CommentResponse(
                id=comment.id,
                post_id=comment.post_id,
                author_id=comment.author_id,
                content=comment.content,
                img_url=comment.img_url,
                created_at=comment.created_at,
            )
            for comment in comments
        ]

        stats = self.post_model.get_post_stats(post.id)

        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            img_url=post.img_url,
            status=PostStatusResponse(
                view_count=stats["view_count"],
                like_count=stats["like_count"],
                comment_count=stats["comment_count"],
            ),
            del_yn=post.del_yn,
            created_at=post.created_at,
            comments=comment_responses,
        )

    def create_post(
        self, request: CreatePostRequest, current_user: User
    ) -> PostResponse:
        """게시글 등록

        Args:
            request: 게시글 등록 요청
            current_user: 인증된 사용자

        Returns:
            PostResponse: 생성된 게시글
        """
        post = self.post_model.create(
            title=request.title,
            content=request.content,
            author_id=current_user.id,
            img_url=request.img_url,
        )
        return self._convert_to_response(post)

    def get_posts(self) -> PostListResponse:
        """게시글 목록 조회"""
        posts = self.post_model.find_posts()
        post_responses = [self._convert_to_response(post) for post in posts]
        return PostListResponse(posts=post_responses, total=len(post_responses))

    def get_post(
        self, post_id: int, current_user: Optional[User] = None
    ) -> PostResponse:
        """게시글 상세 조회 (Aggregate 패턴)"""
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다.",
            error_code=ErrorCode.POST_NOT_FOUND,
        )

        if current_user:
            self.post_model.add_view(post_id, current_user.id)

        return self._convert_to_response(post)

    def update_post(
        self, post_id: int, request: UpdatePostRequest, current_user: User
    ) -> PostResponse:
        """게시글 수정

        Args:
            post_id: 게시글 ID
            request: 수정 요청
            current_user: 인증된 사용자

        Returns:
            PostResponse: 수정된 게시글

        Raises:
            ForbiddenException: 작성자가 아닌 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다.",
            error_code=ErrorCode.POST_NOT_FOUND,
        )

        if post.author_id != current_user.id:
            raise ForbiddenException(
                "게시글을 수정할 권한이 없습니다.",
                error_code=ErrorCode.POST_PERMISSION_DENIED,
            )

        updated_post = self.post_model.update(
            id=post_id,
            title=request.title,
            content=request.content,
            img_url=request.img_url,
        )

        updated_post = get_or_raise(
            updated_post,
            "게시글 수정에 실패했습니다.",
            error_code=ErrorCode.POST_NOT_FOUND,
        )

        return self._convert_to_response(updated_post)

    def delete_post(self, post_id: int, current_user: User) -> None:
        """게시글 삭제

        Args:
            post_id: 게시글 ID
            current_user: 인증된 사용자

        Raises:
            ForbiddenException: 작성자가 아닌 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다.",
            error_code=ErrorCode.POST_NOT_FOUND,
        )

        if post.author_id != current_user.id:
            raise ForbiddenException(
                "게시글을 삭제할 권한이 없습니다.",
                error_code=ErrorCode.POST_PERMISSION_DENIED,
            )

        self.post_model.delete(post_id)

    def like_post(self, post_id: int, current_user: User) -> PostResponse:
        """게시글 좋아요 (Aggregate 패턴)"""
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다.",
            error_code=ErrorCode.POST_NOT_FOUND,
        )

        if not self.post_model.add_like(post_id, current_user.id):
            raise ConflictException(
                "이미 좋아요한 게시글입니다.", error_code=ErrorCode.LIKE_ALREADY_EXISTS
            )

        return self._convert_to_response(post)

    def unlike_post(self, post_id: int, current_user: User) -> PostResponse:
        """게시글 좋아요 취소 (Aggregate 패턴)"""
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다.",
            error_code=ErrorCode.POST_NOT_FOUND,
        )

        if not self.post_model.remove_like(post_id, current_user.id):
            raise BadRequestException(
                "좋아요하지 않은 게시글입니다.", error_code=ErrorCode.LIKE_NOT_FOUND
            )

        return self._convert_to_response(post)

    def add_comment(
        self, post_id: int, request: CreateCommentRequest, current_user: User
    ) -> PostResponse:
        """댓글 생성 (Aggregate 패턴)"""
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다.",
            error_code=ErrorCode.POST_NOT_FOUND,
        )

        self.post_model.add_comment(
            post_id=post_id,
            author_id=current_user.id,
            content=request.content,
            img_url=request.img_url,
        )

        return self._convert_to_response(post)

    def update_comment(
        self,
        id: int,
        comment_id: int,
        request: UpdateCommentRequest,
        current_user: User,
    ) -> PostResponse:
        """댓글 수정 (Aggregate 패턴, 권한 확인 포함)

        Raises:
            ForbiddenException: 작성자가 아닌 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(id),
            "게시글을 찾을 수 없습니다.",
            error_code=ErrorCode.POST_NOT_FOUND,
        )

        updated_comment = self.post_model.update_comment(
            post_id=id,
            comment_id=comment_id,
            content=request.content,
            author_id=current_user.id,
        )

        if not updated_comment:
            raise ForbiddenException(
                "댓글을 수정할 권한이 없습니다.",
                error_code=ErrorCode.COMMENT_PERMISSION_DENIED,
            )

        return self._convert_to_response(post)

    def remove_comment(
        self, id: int, comment_id: int, current_user: User
    ) -> PostResponse:
        """댓글 삭제 (Aggregate 패턴, 권한 확인 포함)

        Raises:
            ForbiddenException: 작성자가 아닌 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(id),
            "게시글을 찾을 수 없습니다.",
            error_code=ErrorCode.POST_NOT_FOUND,
        )

        if not self.post_model.delete_comment(
            post_id=id, comment_id=comment_id, author_id=current_user.id
        ):
            raise ForbiddenException(
                "댓글을 삭제할 권한이 없습니다.",
                error_code=ErrorCode.COMMENT_PERMISSION_DENIED,
            )

        return self._convert_to_response(post)
