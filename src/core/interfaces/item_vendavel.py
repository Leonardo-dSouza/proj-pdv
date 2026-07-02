from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.core.entidades.composicao_item import ComposicaoItem


class ItemVendavel(Protocol):
    def calcular_preco(self) -> Decimal: ...

    def get_composicao(self) -> list[ComposicaoItem]: ...
