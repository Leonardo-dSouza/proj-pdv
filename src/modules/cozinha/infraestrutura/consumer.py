import json

import pika

from src.config.settings import obter_configuracoes
from src.infrastructure.mensageria.fila_pedidos_rabbitmq import NOME_FILA


def processar_mensagem(canal, metodo, propriedades, corpo) -> None:
    mensagem = json.loads(corpo)
    print(
        f"[cozinha] Pedido recebido: {mensagem['pedido_id']} | "
        f"{len(mensagem['itens'])} item(ns) | total R$ {mensagem['valor_total']}"
    )
    canal.basic_ack(delivery_tag=metodo.delivery_tag)


def iniciar_consumo() -> None:
    config = obter_configuracoes()
    conexao = pika.BlockingConnection(pika.URLParameters(config.rabbitmq_url))
    canal = conexao.channel()
    canal.queue_declare(queue=NOME_FILA, durable=True)
    canal.basic_consume(queue=NOME_FILA, on_message_callback=processar_mensagem)
    print("[cozinha] Aguardando pedidos. CTRL+C para sair.")
    canal.start_consuming()


if __name__ == "__main__":
    iniciar_consumo()