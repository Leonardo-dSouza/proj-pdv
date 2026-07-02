import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.entidades.enums import MesaStatus
from src.infrastructure.database import Base


class MesaModel(Base):
    __tablename__ = "mesas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    numero: Mapped[int] = mapped_column(unique=True)
    status: Mapped[MesaStatus] = mapped_column(
        SAEnum(MesaStatus, name="mesa_status_enum", create_type=False),
        default=MesaStatus.LIVRE,
    )