import json

import pika

from src.config.settings import obter_configuracoes

NOME_FILA = "pedidos"


class FilaPedidosRabbitMQ:
    def __init__(self) -> None:
        self._url = obter_configuracoes().rabbitmq_url

    def publicar(self, pedido) -> None:
        mensagem = {
            "pedido_id": str(pedido.id),
            "tipo": pedido.tipo.value,
            "status": pedido.status.value,
            "valor_total": str(pedido.calcular_total()),
            "itens": [
                {"quantidade": item.quantidade, "preco_unitario": str(item.preco_unitario)}
                for item in pedido.itens
            ],
        }
        conexao = pika.BlockingConnection(pika.URLParameters(self._url))
        canal = conexao.channel()
        canal.queue_declare(queue=NOME_FILA, durable=True)
        canal.basic_publish(
            exchange="",
            routing_key=NOME_FILA,
            body=json.dumps(mensagem),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        conexao.close()