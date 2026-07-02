from sqlalchemy import select
from sqlalchemy.orm import Session

from src.modules.caixa.infraestrutura.modelos import CaixaModel


class CaixaRepositorySQLAlchemy:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def existe_caixa_aberto(self) -> bool:
        stmt = select(CaixaModel).where(CaixaModel.status == "ABERTO")
        return self._sessao.execute(stmt).scalar_one_or_none() is not None