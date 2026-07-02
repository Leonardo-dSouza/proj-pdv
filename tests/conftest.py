import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.infrastructure.database import engine
from src.infrastructure import model_registry  

from src.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture
def sessao_db():
    conexao = engine.connect()
    transacao = conexao.begin()
    sessao = Session(bind=conexao, join_transaction_mode="create_savepoint")
    yield sessao
    sessao.close()
    transacao.rollback()
    conexao.close()