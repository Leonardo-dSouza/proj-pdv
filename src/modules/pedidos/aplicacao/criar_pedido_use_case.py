from sqlalchemy.orm import Session

from src.core.entidades.item_pedido import ItemPedido
from src.core.entidades.pedido import Pedido
from src.core.excecoes import CaixaFechadoError
from src.modules.estoque.aplicacao.estoque_service import EstoqueService
from src.modules.pedidos.aplicacao.dtos import CriarPedidoDTO


class CriarPedidoUseCase:
    def __init__(
        self,
        sessao: Session,
        repositorio_produto,
        repositorio_combo,
        repositorio_ingrediente,
        repositorio_caixa,
        repositorio_pedido,
        publicador_eventos,
    ) -> None:
        self._sessao = sessao
        self._repositorio_produto = repositorio_produto
        self._repositorio_combo = repositorio_combo
        self._repositorio_caixa = repositorio_caixa
        self._repositorio_pedido = repositorio_pedido
        self._estoque_service = EstoqueService(repositorio_ingrediente, publicador_eventos)

    def executar(self, dto: CriarPedidoDTO) -> Pedido:
        if not self._repositorio_caixa.existe_caixa_aberto():
            raise CaixaFechadoError("Não é possível criar pedido sem caixa aberto.")

        itens_pedido: list[ItemPedido] = []
        for item_dto in dto.itens:
            if item_dto.tipo == "produto":
                item_vendavel = self._repositorio_produto.obter_por_id(item_dto.item_id)
            else:
                item_vendavel = self._repositorio_combo.obter_por_id(item_dto.item_id)

            itens_pedido.append(
                ItemPedido(
                    item=item_vendavel,
                    quantidade=item_dto.quantidade,
                    preco_unitario=item_vendavel.calcular_preco(),
                )
            )

        pedido = Pedido(tipo=dto.tipo, mesa_id=dto.mesa_id, operador_id=dto.operador_id)
        for item_pedido in itens_pedido:
            pedido.adicionar_item(item_pedido)

        # Baixa de estoque acontece na criação do pedido, não na entrega (ver nota do diagrama).
        self._estoque_service.baixar_para_pedido(itens_pedido)

        self._repositorio_pedido.salvar(pedido)
        self._sessao.commit()
        return pedido