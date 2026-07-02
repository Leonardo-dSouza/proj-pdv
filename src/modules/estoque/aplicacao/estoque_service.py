import uuid
from decimal import Decimal

from src.core.entidades.item_pedido import ItemPedido
from src.core.eventos.alerta_estoque import AlertaEstoque
from src.core.interfaces.ingrediente_repository import IngredienteRepository
from src.core.interfaces.publicador_eventos import PublicadorEventos


class EstoqueService:
    def __init__(
        self,
        repositorio_ingrediente: IngredienteRepository,
        publicador_eventos: PublicadorEventos,
    ) -> None:
        self._repositorio = repositorio_ingrediente
        self._publicador = publicador_eventos

    def baixar_para_pedido(self, itens: list[ItemPedido]) -> None:
        """
        Para cada item do pedido, percorre a composição (recursiva no caso de
        Combo -> Produto[] -> ComposicaoItem[]) e baixa o estoque de cada
        ingrediente proporcionalmente à quantidade vendida.
        """
        for item_pedido in itens:
            composicao = item_pedido.item.get_composicao()
            for composicao_item in composicao:
                self._baixar_ingrediente(
                    ingrediente_id=composicao_item.ingrediente.id,
                    quantidade=composicao_item.quantidade * item_pedido.quantidade,
                )

    def _baixar_ingrediente(self, ingrediente_id: uuid.UUID, quantidade: Decimal) -> None:
        ingrediente = self._repositorio.obter_para_atualizacao(ingrediente_id)
        ingrediente.baixar(quantidade)
        self._repositorio.salvar(ingrediente)

        if ingrediente.quantidade_estoque <= ingrediente.estoque_minimo:
            self._publicador.publicar(
                AlertaEstoque(
                    ingrediente_id=ingrediente.id,
                    nome_ingrediente=ingrediente.nome,
                    quantidade_atual=ingrediente.quantidade_estoque,
                    estoque_minimo=ingrediente.estoque_minimo,
                )
            )