from fastapi import Request


class UserController:
    """사용자 관련 비즈니스 로직 처리"""

    def register(self, request: Request) -> dict:
        """회원가입 처리"""

        return {
            "id": 1,
            "image_url": "https://example.com/profile.jpg",
            "email": "user@example.com",
            "nick_name": "user",
        }

    def login(self, request: Request) -> dict:
        """로그인 처리"""
        return {
            "id": 1,  # 세션 아이디를 리턴해야하지만, 로그인 구현이 없는 관계로 id 값을 리턴한다.
            "image_url": "https://example.com/profile.jpg",
            "email": "user@example.com",
            "nick_name": "user",
        }

    def logout(self) -> dict:
        """로그아웃 처리 (더미 구현 - 항상 성공)"""
        return {"message": "로그아웃되었습니다."}

    def get_profile(self, user_id: int) -> dict:
        """프로필 조회"""

        return {
            "image_url": "https://example.com/profile.jpg",
            "email": "user@example.com",
            "nick_name": "user",
        }

    def update_profile(self, user_id: int, request: Request) -> dict:
        """프로필 수정"""
        return {
            "nick_name": "새로운닉네임",  # 닉네임
            "image_url": "https://example.com/new-profile.jpg",  # 새로운 프로필 이미지 URL #난수 생성
        }

    def delete_user(self, user_id: int) -> dict:

        return {"message": "회원 탈퇴가 완료되었습니다."}
