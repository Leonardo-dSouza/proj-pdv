from typing import Protocol

from src.core.entidades.pedido import Pedido


class FilaPedidosPort(Protocol):
    def publicar(self, pedido: Pedido) -> None: ...