import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class AlertaEstoque:
    ingrediente_id: uuid.UUID
    nome_ingrediente: str
    quantidade_atual: Decimal
    estoque_minimo: Decimal
    data_alerta: datetime = field(default_factory=datetime.now)