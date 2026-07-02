import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from src.core.entidades.enums import StatusPedido, TipoPedido
from src.core.entidades.item_pedido import ItemPedido
from src.core.excecoes import TransicaoStatusInvalidaError

# Regra: CANCELADO é alcançável de qualquer status exceto ENTREGUE.
TRANSICOES_VALIDAS: dict[StatusPedido, set[StatusPedido]] = {
    StatusPedido.ABERTO: {StatusPedido.PREPARO, StatusPedido.CANCELADO},
    StatusPedido.PREPARO: {StatusPedido.PRONTO, StatusPedido.CANCELADO},
    StatusPedido.PRONTO: {StatusPedido.ENTREGUE, StatusPedido.CANCELADO},
    StatusPedido.ENTREGUE: set(),
    StatusPedido.CANCELADO: set(),
}

# Devolve estoque só se o cancelamento ocorrer estando ABERTO ou PREPARO.
STATUS_QUE_DEVOLVEM_ESTOQUE_AO_CANCELAR = {StatusPedido.ABERTO, StatusPedido.PREPARO}


@dataclass
class Pedido:
    tipo: TipoPedido
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    operador_id: uuid.UUID | None = None
    status: StatusPedido = StatusPedido.ABERTO
    data_hora: datetime = field(default_factory=datetime.now)
    itens: list[ItemPedido] = field(default_factory=list)
    taxa_entrega: Decimal = Decimal("0")
    mesa_id: uuid.UUID | None = None


    def adicionar_item(self, item_pedido: ItemPedido) -> None:
        if self.status != StatusPedido.ABERTO:
            raise TransicaoStatusInvalidaError(
                "Só é possível adicionar itens a um pedido ABERTO."
            )
        self.itens.append(item_pedido)

    def remover_item(self, item_pedido: ItemPedido) -> None:
        if self.status != StatusPedido.ABERTO:
            raise TransicaoStatusInvalidaError(
                "Só é possível remover itens de um pedido ABERTO."
            )
        self.itens.remove(item_pedido)

    def calcular_total(self) -> Decimal:
        subtotal_itens = sum((item.subtotal() for item in self.itens), Decimal("0"))
        return subtotal_itens + self.taxa_entrega

    def mudar_status(self, novo_status: StatusPedido) -> None:
        transicoes_permitidas = TRANSICOES_VALIDAS[self.status]
        if novo_status not in transicoes_permitidas:
            raise TransicaoStatusInvalidaError(
                f"Não é possível transicionar de {self.status.value} para {novo_status.value}."
            )
        self.status = novo_status

    def cancelar(self) -> bool:
        """Cancela o pedido e retorna True se o estoque deve ser devolvido."""
        deve_devolver_estoque = self.status in STATUS_QUE_DEVOLVEM_ESTOQUE_AO_CANCELAR
        self.mudar_status(StatusPedido.CANCELADO)
        return deve_devolver_estoque