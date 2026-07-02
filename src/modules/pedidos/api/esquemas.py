import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from src.core.entidades.enums import StatusPedido, TipoPedido


class ItemPedidoRequest(BaseModel):
    tipo: Literal["produto", "combo"]
    item_id: uuid.UUID
    quantidade: int


class CriarPedidoRequest(BaseModel):
    tipo: TipoPedido
    operador_id: uuid.UUID
    mesa_id: uuid.UUID | None = None
    itens: list[ItemPedidoRequest]


class ItemPedidoResponse(BaseModel):
    quantidade: int
    preco_unitario: Decimal
    produto_id: uuid.UUID | None
    combo_id: uuid.UUID | None


class PedidoResponse(BaseModel):
    id: uuid.UUID
    tipo: TipoPedido
    status: StatusPedido
    valor_total: Decimal
    itens: list[ItemPedidoResponse]