from typing import List

from pydantic import BaseModel


class ImageResponse(BaseModel):
    """이미지 응답 DTO"""

    id: int
    url: str
    file_name: str
    file_size: int
    mime_type: str
    entity_type: str
    entity_id: int
    order: int
    uploaded_by: int
    created_at: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "url": "https://example.com/uploads/image.jpg",
                "file_name": "image.jpg",
                "file_size": 102400,
                "mime_type": "image/jpeg",
                "entity_type": "post",
                "entity_id": 1,
                "order": 0,
                "uploaded_by": 1,
                "created_at": "2025-01-13 10:30:00",
            }
        }


class UploadImageResponse(BaseModel):
    """이미지 업로드 응답 DTO"""

    image_id: int
    url: str

    class Config:
        json_schema_extra = {
            "example": {"image_id": 1, "url": "https://example.com/uploads/image.jpg"}
        }


class MultipleUploadImageResponse(BaseModel):
    """다중 이미지 업로드 응답 DTO"""

    images: List[UploadImageResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "images": [
                    {"image_id": 1, "url": "https://example.com/uploads/image1.jpg"},
                    {"image_id": 2, "url": "https://example.com/uploads/image2.jpg"},
                ],
                "total": 2,
            }
        }
