import uuid
from decimal import Decimal

import pytest

from src.core.entidades.enums import TipoPedido
from src.core.excecoes import CaixaFechadoError
from src.modules.caixa.infraestrutura.modelos import CaixaModel
from src.modules.caixa.infraestrutura.repositorios import CaixaRepositorySQLAlchemy
from src.modules.catalogo.infraestrutura.modelos import ComposicaoItemModel, IngredienteModel, ProdutoModel
from src.modules.catalogo.infraestrutura.repositorios import ComboRepositorySQLAlchemy, ProdutoRepositorySQLAlchemy
from src.modules.catalogo.infraestrutura.repositorios import IngredienteRepositorySQLAlchemy 
from src.modules.pedidos.aplicacao.criar_pedido_use_case import CriarPedidoUseCase
from src.modules.pedidos.aplicacao.dtos import CriarPedidoDTO, ItemPedidoDTO
from src.modules.pedidos.infraestrutura.modelos import PedidoModel
from src.modules.pedidos.infraestrutura.repositorios import PedidoRepositorySQLAlchemy


class PublicadorEventosNulo:
    def publicar(self, evento) -> None:
        pass


def test_criar_pedido_balcao_debita_estoque(sessao_db):
    operador_id = uuid.uuid4()
    sessao_db.execute(
        __import__("sqlalchemy").text(
            "INSERT INTO operadores (id, nome, email, senha, perfil) "
            "VALUES (:id, 'Teste', 'teste@teste.com', 'hash', 'ATENDENTE')"
        ),
        {"id": operador_id},
    )
    sessao_db.add(CaixaModel(status="ABERTO"))

    pao = IngredienteModel(nome="Pão", quantidade_estoque=100, valor=1, estoque_minimo=10)
    produto = ProdutoModel(nome="X-Burguer", preco=Decimal("15.00"), ativo=True)
    sessao_db.add_all([pao, produto])
    sessao_db.flush()

    sessao_db.add(ComposicaoItemModel(produto_id=produto.id, ingrediente_id=pao.id, quantidade=1))
    sessao_db.flush()

    use_case = CriarPedidoUseCase(
        sessao=sessao_db,
        repositorio_produto=ProdutoRepositorySQLAlchemy(sessao_db),
        repositorio_combo=ComboRepositorySQLAlchemy(sessao_db),
        repositorio_ingrediente=IngredienteRepositorySQLAlchemy(sessao_db),
        repositorio_caixa=CaixaRepositorySQLAlchemy(sessao_db),
        repositorio_pedido=PedidoRepositorySQLAlchemy(sessao_db),
        publicador_eventos=PublicadorEventosNulo(),
        publicador_fila=PublicadorEventosNulo(),
    )

    dto = CriarPedidoDTO(
        tipo=TipoPedido.BALCAO,
        operador_id=operador_id,
        itens=[ItemPedidoDTO(tipo="produto", item_id=produto.id, quantidade=2)],
    )

    pedido = use_case.executar(dto)

    assert pedido.calcular_total() == Decimal("30.00")
    sessao_db.refresh(pao)
    assert pao.quantidade_estoque == Decimal("98")

    pedido_no_banco = sessao_db.get(PedidoModel, pedido.id)
    assert pedido_no_banco is not None
    assert len(pedido_no_banco.itens) == 1


def test_criar_pedido_sem_caixa_aberto_lanca_excecao(sessao_db):
    sessao_db.execute(
        __import__("sqlalchemy").text(
            "DELETE FROM caixa"
        )
    )
    
    operador_id = uuid.uuid4()
    sessao_db.execute(
        __import__("sqlalchemy").text(
            "INSERT INTO operadores (id, nome, email, senha, perfil) "
            "VALUES (:id, 'Teste', 'teste@teste.com', 'hash', 'ATENDENTE')"
        ),
        {"id": operador_id},
    )

    sessao_db.flush()
    
    use_case = CriarPedidoUseCase(
        sessao=sessao_db,
        repositorio_produto=ProdutoRepositorySQLAlchemy(sessao_db),
        repositorio_combo=ComboRepositorySQLAlchemy(sessao_db),
        repositorio_ingrediente=IngredienteRepositorySQLAlchemy(sessao_db),
        repositorio_caixa=CaixaRepositorySQLAlchemy(sessao_db),
        repositorio_pedido=PedidoRepositorySQLAlchemy(sessao_db),
        publicador_eventos=PublicadorEventosNulo(),
        publicador_fila=PublicadorEventosNulo()
    )
    dto = CriarPedidoDTO(tipo=TipoPedido.BALCAO, operador_id=operador_id, itens=[])

    with pytest.raises(CaixaFechadoError):
        use_case.executar(dto)