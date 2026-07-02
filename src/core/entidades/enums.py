from enum import Enum


class TipoPedido(str, Enum):
    BALCAO = "BALCAO"
    MESA = "MESA"
    RETIRADA = "RETIRADA"
    DELIVERY = "DELIVERY"


class StatusPedido(str, Enum):
    ABERTO = "ABERTO"
    PREPARO = "PREPARO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


class Perfil(str, Enum):
    GERENTE = "GERENTE"
    ATENDENTE = "ATENDENTE"

class MesaStatus(str, Enum):
    LIVRE = "LIVRE"
    OCUPADA = "OCUPADA"
    AGUARDANDO_FECHAMENTO = "AGUARDANDO_FECHAMENTO"