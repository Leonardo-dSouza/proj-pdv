class TransicaoStatusInvalidaError(Exception):
    """Levantada ao tentar mover o pedido para um status não permitido pela máquina de estados."""