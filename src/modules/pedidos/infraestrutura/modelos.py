import datetime
import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum
from src.core.entidades.enums import StatusPedido, TipoPedido

from src.infrastructure.database import Base


class PedidoModel(Base):
    __tablename__ = "pedidos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tipo: Mapped[TipoPedido] = mapped_column(SAEnum(TipoPedido, name="tipo_pedido_enum", create_type=False))
    status: Mapped[StatusPedido] = mapped_column(
        SAEnum(StatusPedido, name="status_pedido_enum", create_type=False),
        default=StatusPedido.ABERTO,
    )
    data_hora: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    valor_total: Mapped[float] = mapped_column(Numeric(10, 2))
    taxa_entrega: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    mesa_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("mesas.id", ondelete="SET NULL"))
    operador_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("operadores.id", ondelete="RESTRICT"))

    itens: Mapped[list["ItemPedidoModel"]] = relationship(back_populates="pedido", cascade="all, delete-orphan")


class ItemPedidoModel(Base):
    __tablename__ = "itens_pedido"
    __table_args__ = (
        CheckConstraint(
            "(produto_id IS NOT NULL AND combo_id IS NULL) OR (produto_id IS NULL AND combo_id IS NOT NULL)",
            name="ck_item_pedido_produto_xor_combo",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    pedido_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pedidos.id", ondelete="CASCADE"))
    produto_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("produtos.id", ondelete="RESTRICT"))
    combo_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("combos.id", ondelete="RESTRICT"))
    quantidade: Mapped[int]
    preco_unitario: Mapped[float] = mapped_column(Numeric(10, 2))
    desconto: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    pedido: Mapped["PedidoModel"] = relationship(back_populates="itens")