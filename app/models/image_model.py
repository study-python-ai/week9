from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Integer, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user_model import User


class ImageType(str, Enum):
    """이미지 타입"""

    USER = "user"
    POST = "post"
    COMMENT = "comment"


class Image(Base, TimestampMixin):
    """이미지 모델"""

    __tablename__ = "tb_image"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("tb_user.id"), nullable=False, index=True
    )

    uploader: Mapped["User"] = relationship("User", foreign_keys=[uploaded_by])


class ImageModel:
    """이미지 데이터 관리"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        url: str,
        file_name: str,
        file_size: int,
        mime_type: str,
        entity_type: str,
        entity_id: int,
        uploaded_by: int,
        order: int = 0,
    ) -> Image:
        """이미지 생성

        Args:
            url: 이미지 URL
            file_name: 파일명
            file_size: 파일 크기
            mime_type: MIME 타입
            entity_type: 엔티티 타입
            entity_id: 엔티티 ID
            uploaded_by: 업로드한 사용자 ID
            order: 순서

        Returns:
            Image: 생성된 이미지
        """
        image = Image(
            url=url,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            entity_type=entity_type,
            entity_id=entity_id,
            uploaded_by=uploaded_by,
            order=order,
        )

        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)

        return image

    def find_by_id(self, image_id: int) -> Optional[Image]:
        """ID로 이미지 조회

        Args:
            image_id: 이미지 ID

        Returns:
            Optional[Image]: 이미지 (없으면 None)
        """
        stmt = select(Image).where(Image.id == image_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_by_entity(self, entity_type: str, entity_id: int) -> List[Image]:
        """엔티티로 이미지 목록 조회

        Args:
            entity_type: 엔티티 타입
            entity_id: 엔티티 ID

        Returns:
            List[Image]: 이미지 목록 (순서대로)
        """
        stmt = (
            select(Image)
            .where(Image.entity_type == entity_type, Image.entity_id == entity_id)
            .order_by(Image.order.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def find_user_profile_image(self, user_id: int) -> Optional[Image]:
        """사용자 프로필 이미지 조회

        Args:
            user_id: 사용자 ID

        Returns:
            Optional[Image]: 프로필 이미지 (없으면 None)
        """
        images = self.find_by_entity(ImageType.USER.value, user_id)
        return images[0] if images else None

    def find_post_images(self, post_id: int) -> List[Image]:
        """게시글 이미지 목록 조회

        Args:
            post_id: 게시글 ID

        Returns:
            List[Image]: 이미지 목록
        """
        return self.find_by_entity(ImageType.POST.value, post_id)

    def find_comment_images(self, comment_id: int) -> List[Image]:
        """댓글 이미지 목록 조회

        Args:
            comment_id: 댓글 ID

        Returns:
            List[Image]: 이미지 목록
        """
        return self.find_by_entity(ImageType.COMMENT.value, comment_id)

    def delete(self, image_id: int) -> bool:
        """이미지 삭제

        Args:
            image_id: 이미지 ID

        Returns:
            bool: 삭제 성공 여부
        """
        image = self.find_by_id(image_id)

        if not image:
            return False

        self.db.delete(image)
        self.db.commit()
        return True

    def delete_by_entity(self, entity_type: str, entity_id: int) -> int:
        """엔티티의 모든 이미지 삭제

        Args:
            entity_type: 엔티티 타입
            entity_id: 엔티티 ID

        Returns:
            int: 삭제된 이미지 수
        """
        images = self.find_by_entity(entity_type, entity_id)

        for image in images:
            self.db.delete(image)

        self.db.commit()
        return len(images)

    def replace_user_profile_image(
        self, user_id: int, url: str, file_name: str, file_size: int, mime_type: str
    ) -> Image:
        """사용자 프로필 이미지 교체

        Args:
            user_id: 사용자 ID
            url: 새 이미지 URL
            file_name: 파일명
            file_size: 파일 크기
            mime_type: MIME 타입

        Returns:
            Image: 생성된 이미지
        """

        # 기존 프로필 이미지 삭제
        self.delete_by_entity(ImageType.USER.value, user_id)

        return self.create(
            url=url,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            entity_type=ImageType.USER.value,
            entity_id=user_id,
            uploaded_by=user_id,
            order=0,
        )

    def update_entity(
        self, image_id: int, entity_type: str, entity_id: int, order: int = 0
    ) -> Optional[Image]:
        """이미지의 엔티티 정보 업데이트

        Args:
            image_id: 이미지 ID
            entity_type: 엔티티 타입
            entity_id: 엔티티 ID
            order: 순서

        Returns:
            Optional[Image]: 업데이트된 이미지 (없으면 None)
        """

        # 이미지 조회
        image = self.find_by_id(image_id)

        if not image:
            return None

        image.entity_type = entity_type
        image.entity_id = entity_id
        image.order = order

        self.db.commit()
        self.db.refresh(image)

        return image

    def create_temporary(
        self, url: str, file_name: str, file_size: int, mime_type: str, uploaded_by: int
    ) -> Image:
        """이미지 생성

        Args:
            url: 이미지 URL
            file_name: 파일명
            file_size: 파일 크기
            mime_type: MIME 타입
            uploaded_by: 업로드한 사용자 ID

        Returns:
            Image: 생성된 임시 이미지 (entity_type='temp', entity_id=0)
        """
        return self.create(
            url=url,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            entity_type="temp",
            entity_id=0,
            uploaded_by=uploaded_by,
            order=0,
        )
