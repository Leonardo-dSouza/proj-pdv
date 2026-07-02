import uuid
from decimal import Decimal

from pydantic import BaseModel

from src.core.entidades.enums import StatusPedido, TipoPedido


class AtualizarStatusRequest(BaseModel):
    status: StatusPedido


class PedidoFilaResponse(BaseModel):
    id: uuid.UUID
    tipo: TipoPedido
    status: StatusPedido
    valor_total: Decimal