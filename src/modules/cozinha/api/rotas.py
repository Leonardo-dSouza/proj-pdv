import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.entidades.enums import StatusPedido
from src.core.entidades.pedido import TRANSICOES_VALIDAS
from src.infrastructure.database import get_db
from src.modules.cozinha.api.esquemas import AtualizarStatusRequest, PedidoFilaResponse
from src.modules.pedidos.infraestrutura.modelos import PedidoModel

router = APIRouter(prefix="/cozinha", tags=["cozinha"])


@router.get("/fila", response_model=list[PedidoFilaResponse])
def visualizar_fila(sessao: Session = Depends(get_db)):
    stmt = (
        select(PedidoModel)
        .where(PedidoModel.status.in_([StatusPedido.ABERTO, StatusPedido.PREPARO]))
        .order_by(PedidoModel.data_hora.asc())
    )
    pedidos = sessao.execute(stmt).scalars().all()
    return [
        PedidoFilaResponse(id=p.id, tipo=p.tipo, status=p.status, valor_total=p.valor_total)
        for p in pedidos
    ]


@router.patch("/pedidos/{pedido_id}/status", response_model=PedidoFilaResponse)
def atualizar_status(pedido_id: uuid.UUID, payload: AtualizarStatusRequest, sessao: Session = Depends(get_db)):
    model = sessao.get(PedidoModel, pedido_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    status_atual = StatusPedido(model.status)
    if payload.status not in TRANSICOES_VALIDAS[status_atual]:
        raise HTTPException(
            status_code=422,
            detail=f"Não é possível ir de {status_atual.value} para {payload.status.value}",
        )

    model.status = payload.status
    sessao.commit()
    sessao.refresh(model)
    return PedidoFilaResponse(id=model.id, tipo=model.tipo, status=model.status, valor_total=model.valor_total)