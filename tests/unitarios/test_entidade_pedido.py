from decimal import Decimal

import pytest

from src.core.entidades.enums import StatusPedido, TipoPedido
from src.core.entidades.item_pedido import ItemPedido
from src.core.entidades.pedido import Pedido
from src.core.entidades.produto import Produto
from src.core.excecoes import TransicaoStatusInvalidaError


def _produto(preco: str) -> Produto:
    return Produto(nome="Produto Teste", preco=Decimal(preco), ativo=True, composicao=[])


def test_criar_pedido_comeca_aberto():
    pedido = Pedido(tipo=TipoPedido.BALCAO)
    assert pedido.status == StatusPedido.ABERTO
    assert pedido.itens == []


def test_adicionar_item_calcula_total():
    pedido = Pedido(tipo=TipoPedido.BALCAO)
    item = ItemPedido(item=_produto("10.00"), quantidade=2, preco_unitario=Decimal("10.00"))
    pedido.adicionar_item(item)
    assert pedido.calcular_total() == Decimal("20.00")


def test_calcular_total_soma_taxa_entrega():
    pedido = Pedido(tipo=TipoPedido.DELIVERY, taxa_entrega=Decimal("5.00"))
    item = ItemPedido(item=_produto("10.00"), quantidade=1, preco_unitario=Decimal("10.00"))
    pedido.adicionar_item(item)
    assert pedido.calcular_total() == Decimal("15.00")


def test_transicao_invalida_lanca_excecao():
    pedido = Pedido(tipo=TipoPedido.BALCAO)
    with pytest.raises(TransicaoStatusInvalidaError):
        pedido.mudar_status(StatusPedido.ENTREGUE)  # não pode pular PREPARO/PRONTO


def test_nao_pode_transicionar_a_partir_de_entregue():
    pedido = Pedido(tipo=TipoPedido.BALCAO)
    pedido.mudar_status(StatusPedido.PREPARO)
    pedido.mudar_status(StatusPedido.PRONTO)
    pedido.mudar_status(StatusPedido.ENTREGUE)
    with pytest.raises(TransicaoStatusInvalidaError):
        pedido.mudar_status(StatusPedido.CANCELADO)


def test_cancelar_em_preparo_devolve_estoque():
    pedido = Pedido(tipo=TipoPedido.BALCAO)
    pedido.mudar_status(StatusPedido.PREPARO)
    deve_devolver = pedido.cancelar()
    assert deve_devolver is True
    assert pedido.status == StatusPedido.CANCELADO


def test_cancelar_em_pronto_nao_devolve_estoque():
    pedido = Pedido(tipo=TipoPedido.BALCAO)
    pedido.mudar_status(StatusPedido.PREPARO)
    pedido.mudar_status(StatusPedido.PRONTO)
    deve_devolver = pedido.cancelar()
    assert deve_devolver is False
    assert pedido.status == StatusPedido.CANCELADO


def test_nao_pode_adicionar_item_fora_de_aberto():
    pedido = Pedido(tipo=TipoPedido.BALCAO)
    pedido.mudar_status(StatusPedido.PREPARO)
    item = ItemPedido(item=_produto("10.00"), quantidade=1, preco_unitario=Decimal("10.00"))
    with pytest.raises(TransicaoStatusInvalidaError):
        pedido.adicionar_item(item)