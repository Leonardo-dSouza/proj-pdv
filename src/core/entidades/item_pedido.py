from dataclasses import dataclass
from decimal import Decimal

from src.core.interfaces.item_vendavel import ItemVendavel


@dataclass
class ItemPedido:
    item: ItemVendavel
    quantidade: int
    preco_unitario: Decimal
    desconto: Decimal = Decimal("0")

    def subtotal(self) -> Decimal:
        bruto = self.preco_unitario * self.quantidade
        liquido = bruto - self.desconto
        return liquido if liquido > Decimal("0") else Decimal("0")