from fastapi import Request


class PostController:
    """게시글 관련 비즈니스 로직 처리"""

    def create_post(self, request: Request) -> dict:
        """게시글 등록"""
        return {
            "id": 1,
            "title": "FastAPI 게시글 제목",
            "content": "FastAPI로 게시판을 만들어봅시다.",
            "author_id": 1,
            "img_url": "https://example.com/image.jpg",
            "status": {"view_count": 42, "like_count": 10, "comment_count": 5},
            "del_yn": "N",
            "created_at": "2025-01-13T10:30:00",
            "comments": [
                {
                    "id": 1,
                    "post_id": 1,
                    "author_id": 2,
                    "img_url": "https://example.com/profile.jpg",
                    "content": "첫 번째 댓글입니다.",
                }
            ],
        }

    def get_posts(self) -> dict:
        """게시글 목록 조회"""

        return {
            "posts": [
                {
                    "id": 1,
                    "title": "첫 번째 게시글",
                    "content": "내용...",
                    "author_id": 1,
                    "img_url": None,
                    "status": {"view_count": 10, "like_count": 2, "comment_count": 0},
                    "del_yn": "N",
                    "created_at": "2025-01-13T10:30:00",
                    "comments": [],
                }
            ],
            "total": 1,
        }

    def get_post(self, post_id: int) -> dict:
        """게시글 상세 조회"""
        # 게시글 존재 여부 확인

        # 게시글 조회 수 증가

        return {
            "id": 1,
            "title": "FastAPI 게시글 제목",
            "content": "FastAPI로 게시판을 만들어봅시다.",
            "author_id": 1,
            "img_url": "https://example.com/image.jpg",
            "status": {"view_count": 42, "like_count": 10, "comment_count": 5},
            "del_yn": "N",
            "created_at": "2025-01-13T10:30:00",
            "comments": [
                {
                    "id": 1,
                    "post_id": 1,
                    "author_id": 2,
                    "img_url": "https://example.com/profile.jpg",
                    "content": "첫 번째 댓글입니다.",
                }
            ],
        }

    def update_post(self, post_id: int, request: Request) -> dict:
        """게시글 수정"""

        # 게시글 존재 여부 확인

        # 작성자 권한 확인

        # 게시글 수정

        # 게시글 실패시 예외 처리

        return {
            "id": 1,
            "title": "FastAPI 게시글 제목",
            "content": "FastAPI로 게시판을 만들어봅시다.",
            "author_id": 1,
            "img_url": "https://example.com/image.jpg",
            "status": {"view_count": 42, "like_count": 10, "comment_count": 5},
            "del_yn": "N",
            "created_at": "2025-01-13T10:30:00",
            "comments": [
                {
                    "id": 1,
                    "post_id": 1,
                    "author_id": 2,
                    "img_url": "https://example.com/profile.jpg",
                    "content": "첫 번째 댓글입니다.",
                }
            ],
        }

    def delete_post(self, post_id: int, author_id: int) -> dict:
        """게시글 삭제"""

        # 게시글 존재 여부 확인

        return {}

    def like_post(self, post_id: int) -> dict:
        """게시글 좋아요 증가"""

        # 게시글 존재 여부 확인

        # 좋아요 수 증가

        return {
            "id": 1,
            "title": "FastAPI 게시글 제목",
            "content": "FastAPI로 게시판을 만들어봅시다.",
            "author_id": 1,
            "img_url": "https://example.com/image.jpg",
            "status": {"view_count": 42, "like_count": 10, "comment_count": 5},
            "del_yn": "N",
            "created_at": "2025-01-13T10:30:00",
            "comments": [
                {
                    "id": 1,
                    "post_id": 1,
                    "author_id": 2,
                    "img_url": "https://example.com/profile.jpg",
                    "content": "첫 번째 댓글입니다.",
                }
            ],
        }

    def unlike_post(self, post_id: int) -> dict:
        """게시글 좋아요 감소"""

        # 게시글 존재 여부 확인

        # 좋아요 수 감소

        return {
            "id": 1,
            "title": "FastAPI 게시글 제목",
            "content": "FastAPI로 게시판을 만들어봅시다.",
            "author_id": 1,
            "img_url": "https://example.com/image.jpg",
            "status": {"view_count": 42, "like_count": 10, "comment_count": 5},
            "del_yn": "N",
            "created_at": "2025-01-13T10:30:00",
            "comments": [
                {
                    "id": 1,
                    "post_id": 1,
                    "author_id": 2,
                    "img_url": "https://example.com/profile.jpg",
                    "content": "첫 번째 댓글입니다.",
                }
            ],
        }

    def add_comment(self, post_id: int, request: Request) -> dict:
        """댓글 생성"""

        # 게시글 존재 여부 확인

        # 작성자 존재 여부 확인

        # 댓글 생성

        # 댓글 수 증가

        return {
            "id": 1,
            "title": "FastAPI 게시글 제목",
            "content": "FastAPI로 게시판을 만들어봅시다.",
            "author_id": 1,
            "img_url": "https://example.com/image.jpg",
            "status": {"view_count": 42, "like_count": 10, "comment_count": 5},
            "del_yn": "N",
            "created_at": "2025-01-13T10:30:00",
            "comments": [
                {
                    "id": 1,
                    "post_id": 1,
                    "author_id": 2,
                    "img_url": "https://example.com/profile.jpg",
                    "content": "첫 번째 댓글입니다.",
                }
            ],
        }

    def update_comment(self, post_id: int, comment_id: int, request: Request) -> dict:
        """댓글 수정 (작성자만 가능)"""

        return {
            "id": 1,
            "title": "FastAPI 게시글 제목",
            "content": "FastAPI로 게시판을 만들어봅시다.",
            "author_id": 1,
            "img_url": "https://example.com/image.jpg",
            "status": {"view_count": 42, "like_count": 10, "comment_count": 5},
            "del_yn": "N",
            "created_at": "2025-01-13T10:30:00",
            "comments": [
                {
                    "id": 1,
                    "post_id": 1,
                    "author_id": 2,
                    "img_url": "https://example.com/profile.jpg",
                    "content": "첫 번째 댓글입니다.",
                }
            ],
        }

    def remove_comment(self, post_id: int, comment_id: int, author_id: int) -> dict:
        """댓글 삭제 (작성자만 가능)"""

        return {
            "id": 1,
            "title": "FastAPI 게시글 제목",
            "content": "FastAPI로 게시판을 만들어봅시다.",
            "author_id": 1,
            "img_url": "https://example.com/image.jpg",
            "status": {"view_count": 42, "like_count": 10, "comment_count": 5},
            "del_yn": "N",
            "created_at": "2025-01-13T10:30:00",
            "comments": [
                {
                    "id": 1,
                    "post_id": 1,
                    "author_id": 2,
                    "img_url": "https://example.com/profile.jpg",
                    "content": "첫 번째 댓글입니다.",
                }
            ],
        }
