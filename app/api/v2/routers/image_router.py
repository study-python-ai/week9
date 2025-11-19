from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.v2.controllers.image_controller import ImageController
from app.core.db.dependencies import get_db, get_image_model
from app.core.security.dependencies import get_current_user
from app.models.user_model import User
from app.schemas.image_schema import ImageResponse, UploadImageResponse

router = APIRouter(prefix="/api/v2/images", tags=["v2-images"])


def get_image_controller(db: Session = Depends(get_db)) -> ImageController:
    """ImageController 의존성 주입 함수

    Args:
        db: 데이터베이스 세션

    Returns:
        ImageController: 이미지 컨트롤러 인스턴스
    """
    return ImageController(get_image_model(db))


@router.post(
    "", response_model=UploadImageResponse, status_code=status.HTTP_201_CREATED
)
def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    controller: ImageController = Depends(get_image_controller),
):
    """단일 이미지 업로드

    Args:
        file: 업로드할 이미지 파일
        current_user: 인증된 사용자
        controller: 이미지 컨트롤러

    Returns:
        UploadImageResponse: 업로드된 이미지 정보
    """
    return controller.upload_image(file, current_user)


@router.get("/{image_id}", response_model=ImageResponse)
def get_image(
    image_id: int, controller: ImageController = Depends(get_image_controller)
):
    """이미지 정보 조회

    Args:
        image_id: 이미지 ID
        controller: 이미지 컨트롤러

    Returns:
        ImageResponse: 이미지 정보
    """
    return controller.get_image(image_id)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    controller: ImageController = Depends(get_image_controller),
):
    """이미지 삭제

    Args:
        image_id: 이미지 ID
        current_user: 인증된 사용자
        controller: 이미지 컨트롤러
    """
    controller.delete_image(image_id, current_user)
