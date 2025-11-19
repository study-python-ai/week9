from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[str] = mapped_column(
        String, default=lambda: datetime.now().isoformat(), nullable=False
    )
    updated_at: Mapped[str] = mapped_column(
        String,
        default=lambda: datetime.now().isoformat(),
        onupdate=lambda: datetime.now().isoformat(),
        nullable=False,
    )


class SoftDeleteMixin:
    del_yn: Mapped[str] = mapped_column(String(1), default="N", nullable=False)

    @classmethod
    def active_filter(cls):
        return cls.del_yn == "N"

    def soft_delete(self) -> None:
        self.del_yn = "Y"
        self.updated_at = datetime.now().isoformat()

    def is_deleted(self) -> bool:
        return self.del_yn == "Y"

    def is_active(self) -> bool:
        return self.del_yn == "N"
