import uuid
from decimal import Decimal

import pytest

from src.core.entidades.combo import Combo
from src.core.entidades.composicao_item import ComposicaoItem
from src.core.entidades.ingrediente import Ingrediente
from src.core.entidades.item_pedido import ItemPedido
from src.core.entidades.produto import Produto
from src.core.excecoes.estoque import EstoqueInsuficienteError
from src.modules.estoque.aplicacao.estoque_service import EstoqueService


class RepositorioIngredienteFalso:
    """Fake em memória — só pra testar a lógica do service, sem banco."""

    def __init__(self, ingredientes: dict[uuid.UUID, Ingrediente]) -> None:
        self._ingredientes = ingredientes
        self.salvos: list[Ingrediente] = []

    def obter_para_atualizacao(self, ingrediente_id: uuid.UUID) -> Ingrediente:
        return self._ingredientes[ingrediente_id]

    def salvar(self, ingrediente: Ingrediente) -> None:
        self.salvos.append(ingrediente)


class PublicadorEventosFalso:
    def __init__(self) -> None:
        self.eventos_publicados: list = []

    def publicar(self, evento) -> None:
        self.eventos_publicados.append(evento)


def _ingrediente(nome: str, quantidade: str, minimo: str = "0") -> Ingrediente:
    return Ingrediente(
        id=uuid.uuid4(),
        nome=nome,
        quantidade_estoque=Decimal(quantidade),
        valor=Decimal("1.00"),
        estoque_minimo=Decimal(minimo),
    )


def test_baixa_simples_debita_estoque():
    pao = _ingrediente("Pão", "100")
    produto = Produto(
        id=uuid.uuid4(), nome="X-Burguer", preco=Decimal("15.00"), ativo=True,
        composicao=[ComposicaoItem(ingrediente=pao, quantidade=Decimal("1"))],
    )
    item_pedido = ItemPedido(item=produto, quantidade=2, preco_unitario=Decimal("15.00"))

    repo = RepositorioIngredienteFalso({pao.id: pao})
    service = EstoqueService(repo, PublicadorEventosFalso())

    service.baixar_para_pedido([item_pedido])

    assert pao.quantidade_estoque == Decimal("98")
    assert len(repo.salvos) == 1


def test_baixa_recursiva_de_combo():
    pao = _ingrediente("Pão", "100")
    queijo = _ingrediente("Queijo", "50")
    x_burguer = Produto(
        id=uuid.uuid4(), nome="X-Burguer", preco=Decimal("15.00"), ativo=True,
        composicao=[ComposicaoItem(ingrediente=pao, quantidade=Decimal("1"))],
    )
    x_salada = Produto(
        id=uuid.uuid4(), nome="X-Salada", preco=Decimal("17.00"), ativo=True,
        composicao=[
            ComposicaoItem(ingrediente=pao, quantidade=Decimal("1")),
            ComposicaoItem(ingrediente=queijo, quantidade=Decimal("2")),
        ],
    )
    combo = Combo(id=uuid.uuid4(), nome="Combo Duplo", desconto=Decimal("5.00"),
                   itens=[x_burguer, x_salada])
    item_pedido = ItemPedido(item=combo, quantidade=1, preco_unitario=combo.calcular_preco())

    repo = RepositorioIngredienteFalso({pao.id: pao, queijo.id: queijo})
    service = EstoqueService(repo, PublicadorEventosFalso())

    service.baixar_para_pedido([item_pedido])

    assert pao.quantidade_estoque == Decimal("98")     # 1 do x-burguer + 1 do x-salada
    assert queijo.quantidade_estoque == Decimal("48")   # 2 do x-salada


def test_estoque_insuficiente_lanca_excecao():
    pao = _ingrediente("Pão", "1")
    produto = Produto(
        id=uuid.uuid4(), nome="X-Burguer", preco=Decimal("15.00"), ativo=True,
        composicao=[ComposicaoItem(ingrediente=pao, quantidade=Decimal("1"))],
    )
    item_pedido = ItemPedido(item=produto, quantidade=5, preco_unitario=Decimal("15.00"))

    repo = RepositorioIngredienteFalso({pao.id: pao})
    service = EstoqueService(repo, PublicadorEventosFalso())

    with pytest.raises(EstoqueInsuficienteError):
        service.baixar_para_pedido([item_pedido])


def test_publica_alerta_quando_estoque_atinge_minimo():
    pao = _ingrediente("Pão", "10", minimo="5")
    produto = Produto(
        id=uuid.uuid4(), nome="X-Burguer", preco=Decimal("15.00"), ativo=True,
        composicao=[ComposicaoItem(ingrediente=pao, quantidade=Decimal("1"))],
    )
    item_pedido = ItemPedido(item=produto, quantidade=5, preco_unitario=Decimal("15.00"))

    repo = RepositorioIngredienteFalso({pao.id: pao})
    publicador = PublicadorEventosFalso()
    service = EstoqueService(repo, publicador)

    service.baixar_para_pedido([item_pedido])

    assert pao.quantidade_estoque == Decimal("5")
    assert len(publicador.eventos_publicados) == 1
    assert publicador.eventos_publicados[0].ingrediente_id == pao.id