import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db
from src.infrastructure.mensageria.fila_pedidos_rabbitmq import FilaPedidosRabbitMQ
from src.modules.caixa.infraestrutura.repositorios import CaixaRepositorySQLAlchemy
from src.modules.catalogo.infraestrutura.repositorios import (
    ComboRepositorySQLAlchemy,
    IngredienteRepositorySQLAlchemy,
    ProdutoRepositorySQLAlchemy,
)
from src.modules.pedidos.api.esquemas import CriarPedidoRequest, ItemPedidoResponse, PedidoResponse
from src.modules.pedidos.aplicacao.criar_pedido_use_case import CriarPedidoUseCase
from src.modules.pedidos.aplicacao.dtos import CriarPedidoDTO, ItemPedidoDTO
from src.modules.pedidos.infraestrutura.modelos import PedidoModel
from src.modules.pedidos.infraestrutura.repositorios import PedidoRepositorySQLAlchemy

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


class _PublicadorEventosNulo:
    def publicar(self, evento) -> None:
        pass  # AlertaEstoque ainda não tem consumidor — Épico 6


def _model_para_response(model: PedidoModel) -> PedidoResponse:
    return PedidoResponse(
        id=model.id,
        tipo=model.tipo,
        status=model.status,
        valor_total=model.valor_total,
        itens=[
            ItemPedidoResponse(
                quantidade=i.quantidade,
                preco_unitario=i.preco_unitario,
                produto_id=i.produto_id,
                combo_id=i.combo_id,
            )
            for i in model.itens
        ],
    )


@router.post("", response_model=PedidoResponse, status_code=201)
def criar_pedido(payload: CriarPedidoRequest, sessao: Session = Depends(get_db)):
    use_case = CriarPedidoUseCase(
        sessao=sessao,
        repositorio_produto=ProdutoRepositorySQLAlchemy(sessao),
        repositorio_combo=ComboRepositorySQLAlchemy(sessao),
        repositorio_ingrediente=IngredienteRepositorySQLAlchemy(sessao),
        repositorio_caixa=CaixaRepositorySQLAlchemy(sessao),
        repositorio_pedido=PedidoRepositorySQLAlchemy(sessao),
        publicador_eventos=_PublicadorEventosNulo(),
        publicador_fila=FilaPedidosRabbitMQ(),
    )
    dto = CriarPedidoDTO(
        tipo=payload.tipo,
        operador_id=payload.operador_id,
        mesa_id=payload.mesa_id,
        itens=[ItemPedidoDTO(tipo=i.tipo, item_id=i.item_id, quantidade=i.quantidade) for i in payload.itens],
    )
    pedido = use_case.executar(dto)

    model = sessao.get(PedidoModel, pedido.id)
    return _model_para_response(model)


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obter_pedido(pedido_id: uuid.UUID, sessao: Session = Depends(get_db)):
    model = sessao.get(PedidoModel, pedido_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return _model_para_response(model)