from app.schemas.post_schema import (
    CreatePostRequest,
    UpdatePostRequest,
    PostResponse,
    PostListResponse,
    PostStatusResponse,
    CreateCommentRequest,
    UpdateCommentRequest,
    CommentResponse,
)
from app.models.post_model import PostModel, Post
from app.models.user_model import UserModel
from app.models.comment_model import CommentModel
from app.common.exceptions import NotFoundException
from app.common.validators import get_or_raise, verify_ownership


class PostController:
    """게시글 관련 비즈니스 로직 처리"""

    def __init__(self, user_model: UserModel = None, comment_model: CommentModel = None):
        self.post_model = PostModel()
        self.user_model = user_model if user_model else UserModel()
        self.comment_model = comment_model if comment_model else CommentModel()

    def _convert_to_response(self, post: Post) -> PostResponse:
        """Post 객체를 PostResponse로 변환

        Args:
            post: Post 모델 객체

        Returns:
            PostResponse: 변환된 응답 객체
        """
        comments = self.comment_model.find_by_post_id(post.id)
        comment_responses = [
            CommentResponse(
                id=comment.id,
                post_id=comment.post_id,
                author_id=comment.author_id,
                content=comment.content,
                img_url=comment.img_url,
                created_at=comment.created_at
            )
            for comment in comments
        ]

        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            author_id=post.author_id,
            img_url=post.img_url,
            status=PostStatusResponse(
                view_count=post.view_count,
                like_count=post.like_count,
                comment_count=post.comment_count
            ),
            del_yn=post.del_yn,
            created_at=post.created_at,
            comments=comment_responses
        )

    def create_post(self, request: CreatePostRequest) -> PostResponse:
        """게시글 등록

        Args:
            request: 게시글 등록 요청 정보
                - title: 게시글 제목
                - content: 게시글 내용
                - author_id: 작성자 ID
                - img_url: 이미지 URL (선택)

        Returns:
            PostResponse: 생성된 게시글 정보

        Raises:
            NotFoundException: 작성자(author_id)가 존재하지 않는 경우
        """
        get_or_raise(
            self.user_model.find_by_id(request.author_id),
            "존재하지 않는 사용자입니다."
        )

        post = self.post_model.create(
            title=request.title,
            content=request.content,
            author_id=request.author_id,
            img_url=request.img_url,
        )
        return self._convert_to_response(post)

    def get_posts(self) -> PostListResponse:
        """게시글 목록 조회

        Returns:
            PostListResponse: 게시글 목록 및 총 개수
        """
        posts = self.post_model.get_all()
        post_responses = [self._convert_to_response(post) for post in posts]
        return PostListResponse(posts=post_responses, total=len(post_responses))

    def get_post(self, post_id: int) -> PostResponse:
        """게시글 상세 조회 (조회수 증가)

        Args:
            post_id: 게시글 ID

        Returns:
            PostResponse: 게시글 정보

        Raises:
            NotFoundException: 게시글을 찾을 수 없는 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다."
        )

        self.post_model.increase_view_count(post_id)

        return self._convert_to_response(post)

    def update_post(self, post_id: int, request: UpdatePostRequest) -> PostResponse:
        """게시글 수정 (작성자만 가능)

        Args:
            post_id: 게시글 ID
            request: 게시글 수정 요청 정보
                - title: 게시글 제목 (선택)
                - content: 게시글 내용 (선택)
                - img_url: 이미지 URL (선택)
                - author_id: 요청자 ID (권한 검증용)

        Returns:
            PostResponse: 수정된 게시글 정보

        Raises:
            NotFoundException: 게시글을 찾을 수 없는 경우
            UnauthorizedException: 작성자가 아닌 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다."
        )

        verify_ownership(
            post.author_id,
            request.author_id,
            "게시글 수정 권한이 없습니다."
        )

        updated_post = self.post_model.update(
            post_id=post_id,
            title=request.title,
            content=request.content,
            img_url=request.img_url,
        )

        return self._convert_to_response(updated_post)

    def delete_post(self, post_id: int, author_id: int) -> dict:
        """게시글 삭제 (작성자만 가능)

        Args:
            post_id: 게시글 ID
            author_id: 요청자 ID (권한 검증용)

        Returns:
            dict: 성공 메시지

        Raises:
            NotFoundException: 게시글을 찾을 수 없는 경우
            UnauthorizedException: 작성자가 아닌 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다."
        )

        verify_ownership(
            post.author_id,
            author_id,
            "게시글 삭제 권한이 없습니다."
        )

        self.post_model.delete(post_id)

        return {"message": "게시글이 삭제되었습니다."}

    def like_post(self, post_id: int) -> PostResponse:
        """게시글 좋아요 증가

        Args:
            post_id: 게시글 ID

        Returns:
            PostResponse: 좋아요 수가 증가된 게시글 정보

        Raises:
            NotFoundException: 게시글을 찾을 수 없는 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다."
        )

        self.post_model.increase_like_count(post_id)

        return self._convert_to_response(post)

    def unlike_post(self, post_id: int) -> PostResponse:
        """게시글 좋아요 감소

        Args:
            post_id: 게시글 ID

        Returns:
            PostResponse: 좋아요 수가 감소된 게시글 정보

        Raises:
            NotFoundException: 게시글을 찾을 수 없는 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다."
        )

        self.post_model.decrease_like_count(post_id)

        return self._convert_to_response(post)

    def add_comment(self, post_id: int, request: CreateCommentRequest) -> PostResponse:
        """댓글 생성

        Args:
            post_id: 게시글 ID
            request: 댓글 생성 요청 정보
                - content: 댓글 내용
                - author_id: 작성자 ID
                - img_url: 프로필 이미지 URL (선택)

        Returns:
            PostResponse: 댓글이 추가된 게시글 정보

        Raises:
            NotFoundException: 게시글 또는 작성자를 찾을 수 없는 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다."
        )

        get_or_raise(
            self.user_model.find_by_id(request.author_id),
            "존재하지 않는 사용자입니다."
        )

        comment = self.comment_model.create(
            post_id=post_id,
            author_id=request.author_id,
            content=request.content,
            img_url=request.img_url
        )

        return self._convert_to_response(post)

    def update_comment(self, post_id: int, comment_id: int, request: UpdateCommentRequest) -> PostResponse:
        """댓글 수정 (작성자만 가능)

        Args:
            post_id: 게시글 ID
            comment_id: 댓글 ID
            request: 댓글 수정 요청 정보
                - content: 댓글 내용
                - author_id: 요청자 ID (권한 검증용)

        Returns:
            PostResponse: 댓글이 수정된 게시글 정보

        Raises:
            NotFoundException: 게시글 또는 댓글을 찾을 수 없는 경우
            UnauthorizedException: 작성자가 아닌 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다."
        )

        comment = get_or_raise(
            self.comment_model.find_by_id(comment_id),
            "댓글을 찾을 수 없습니다."
        )

        if comment.post_id != post_id:
            raise NotFoundException("해당 게시글의 댓글이 아닙니다.")

        verify_ownership(
            comment.author_id,
            request.author_id,
            "댓글 수정 권한이 없습니다."
        )

        self.comment_model.update(comment_id, request.content)

        return self._convert_to_response(post)

    def remove_comment(self, post_id: int, comment_id: int, author_id: int) -> PostResponse:
        """댓글 삭제 (작성자만 가능)

        Args:
            post_id: 게시글 ID
            comment_id: 댓글 ID
            author_id: 요청자 ID (권한 검증용)

        Returns:
            PostResponse: 댓글이 삭제된 게시글 정보

        Raises:
            NotFoundException: 게시글 또는 댓글을 찾을 수 없는 경우
            UnauthorizedException: 작성자가 아닌 경우
        """
        post = get_or_raise(
            self.post_model.find_by_id(post_id),
            "게시글을 찾을 수 없습니다."
        )

        comment = get_or_raise(
            self.comment_model.find_by_id(comment_id),
            "댓글을 찾을 수 없습니다."
        )

        if comment.post_id != post_id:
            raise NotFoundException("해당 게시글의 댓글이 아닙니다.")

        verify_ownership(
            comment.author_id,
            author_id,
            "댓글 삭제 권한이 없습니다."
        )

        self.comment_model.delete(comment_id)

        return self._convert_to_response(post)
