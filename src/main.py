from fastapi import FastAPI

import src.infrastructure.model_registry  

from src.config.settings import obter_configuracoes
from src.modules.catalogo.api.rotas import router as produtos_router
from src.modules.catalogo.api.rotas import router_ingredientes
from src.modules.cozinha.api.rotas import router as cozinha_router
from src.modules.pedidos.api.rotas import router as pedidos_router

config = obter_configuracoes()

app = FastAPI(title="PDV Backend")
app.include_router(produtos_router)
app.include_router(router_ingredientes)
app.include_router(pedidos_router)
app.include_router(cozinha_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "ambiente": config.ambiente}