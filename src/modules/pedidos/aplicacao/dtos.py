import uuid
from dataclasses import dataclass
from typing import Literal

from src.core.entidades.enums import TipoPedido


@dataclass
class ItemPedidoDTO:
    tipo: Literal["produto", "combo"]
    item_id: uuid.UUID
    quantidade: int


@dataclass
class CriarPedidoDTO:
    tipo: TipoPedido
    operador_id: uuid.UUID
    itens: list[ItemPedidoDTO]
    mesa_id: uuid.UUID | None = None