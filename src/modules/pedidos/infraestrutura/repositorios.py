from sqlalchemy.orm import Session

from src.core.entidades.combo import Combo
from src.core.entidades.pedido import Pedido
from src.core.entidades.produto import Produto
from src.modules.pedidos.infraestrutura.modelos import ItemPedidoModel, PedidoModel


class PedidoRepositorySQLAlchemy:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def salvar(self, pedido: Pedido) -> None:
        model = PedidoModel(
            id=pedido.id,
            tipo=pedido.tipo.value,
            status=pedido.status.value,
            data_hora=pedido.data_hora,
            valor_total=pedido.calcular_total(),
            taxa_entrega=pedido.taxa_entrega,
            mesa_id=pedido.mesa_id,
            operador_id=pedido.operador_id,
        )
        for item_pedido in pedido.itens:
            item_model = ItemPedidoModel(
                quantidade=item_pedido.quantidade,
                preco_unitario=item_pedido.preco_unitario,
                desconto=item_pedido.desconto,
                produto_id=item_pedido.item.id if isinstance(item_pedido.item, Produto) else None,
                combo_id=item_pedido.item.id if isinstance(item_pedido.item, Combo) else None,
            )
            model.itens.append(item_model)

        self._sessao.add(model)
        self._sessao.flush()