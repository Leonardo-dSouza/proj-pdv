class ItemNaoEncontradoError(Exception):

    """Levantada quando produto/combo referenciado no pedido não existe."""

class CaixaFechadoError(Exception):

    """Levantada ao tentar criar pedido sem caixa aberto."""

class TransicaoStatusInvalidaError(Exception):
    """Levantada ao tentar mover o pedido para um status não permitido pela máquina de estados."""