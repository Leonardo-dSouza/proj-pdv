import datetime
import uuid

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database import Base


class CaixaModel(Base):
    __tablename__ = "caixa"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    status: Mapped[str]
    horario_abertura: Mapped[datetime.datetime | None]
    data_abertura: Mapped[datetime.date | None]
    data_fechamento: Mapped[datetime.datetime | None]
    valor_abertura: Mapped[float | None] = mapped_column(Numeric(10, 2))
    horario_programado: Mapped[datetime.time | None]
    operador_abertura_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("operadores.id"))
    operador_fechamento_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("operadores.id"))