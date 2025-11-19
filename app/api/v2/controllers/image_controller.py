from fastapi import UploadFile

from app.core.exceptions.error_codes import ErrorCode
from app.core.exceptions.exceptions import BadRequestException
from app.core.validators import get_or_raise
from app.models.image_model import ImageModel
from app.models.user_model import User
from app.schemas.image_schema import ImageResponse, UploadImageResponse


class ImageController:
    """이미지 컨트롤러"""

    def __init__(self, image_model: ImageModel):
        self.image_model = image_model

    def _save_file(self, file: UploadFile) -> tuple[str, int]:
        """파일을 저장하고 URL과 크기 반환

        Args:
            file: 업로드된 파일

        Returns:
            tuple[str, int]: (저장된 URL, 파일 크기)
        """
        # TODO: 실제 파일 저장 로직 구현
        # 1. 파일 유효성 검사 (크기, 타입 등)
        # 2. S3/로컬 스토리지에 저장 하면 좋겠다 ~~~~~~
        # 3. URL 생성

        # 임시 구현 (실제로는 파일을 저장하고 URL 반환)
        file_size = 0
        if file.file:
            content = file.file.read()
            file_size = len(content)
            file.file.seek(0)

        url = f"https://localhost:8000/uploads/{file.filename}"
        return url, file_size

    def upload_image(self, file: UploadFile, current_user: User) -> UploadImageResponse:
        """단일 이미지 업로드

        Args:
            file: 업로드된 파일
            current_user: 인증된 사용자

        Returns:
            UploadImageResponse: 업로드된 이미지 정보

        Raises:
            BadRequestException: 파일이 없거나 유효하지 않은 경우
        """
        if not file:
            raise BadRequestException(
                "파일이 없습니다.", error_code=ErrorCode.INVALID_REQUEST
            )

        if not file.content_type or not file.content_type.startswith("image/"):
            raise BadRequestException(
                "이미지 파일만 업로드 가능합니다.", error_code=ErrorCode.INVALID_REQUEST
            )

        url, file_size = self._save_file(file)

        image = self.image_model.create_temporary(
            url=url,
            file_name=file.filename or "unknown",
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream",
            uploaded_by=current_user.id,
        )

        return UploadImageResponse(image_id=image.id, url=image.url)

    def get_image(self, image_id: int) -> ImageResponse:
        """이미지 정보 조회

        Args:
            image_id: 이미지 ID

        Returns:
            ImageResponse: 이미지 정보

        Raises:
            NotFoundException: 이미지를 찾을 수 없는 경우
        """
        image = get_or_raise(
            self.image_model.find_by_id(image_id),
            "이미지를 찾을 수 없습니다.",
            error_code=ErrorCode.NOT_FOUND,
        )

        return ImageResponse.model_validate(image)

    def delete_image(self, image_id: int, current_user: User) -> None:
        """이미지 삭제

        Args:
            image_id: 이미지 ID
            current_user: 인증된 사용자

        Raises:
            NotFoundException: 이미지를 찾을 수 없는 경우
            BadRequestException: 삭제 권한이 없는 경우
        """
        image = get_or_raise(
            self.image_model.find_by_id(image_id),
            "이미지를 찾을 수 없습니다.",
            error_code=ErrorCode.NOT_FOUND,
        )

        if image.uploaded_by != current_user.id:
            raise BadRequestException(
                "이미지를 삭제할 권한이 없습니다.", error_code=ErrorCode.FORBIDDEN
            )

        self.image_model.delete(image_id)
