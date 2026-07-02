import datetime
import uuid

from sqlalchemy import Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.entidades.enums import Perfil
from src.infrastructure.database import Base


class OperadorModel(Base):
    __tablename__ = "operadores"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nome: Mapped[str]
    email: Mapped[str] = mapped_column(String, unique=True)
    senha: Mapped[str]
    perfil: Mapped[Perfil] = mapped_column(SAEnum(Perfil, name="perfil_enum", create_type=False))
    criado_em: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)