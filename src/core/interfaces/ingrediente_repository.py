import uuid
from typing import Protocol

from src.core.entidades.ingrediente import Ingrediente


class IngredienteRepository(Protocol):
    def obter_para_atualizacao(self, ingrediente_id: uuid.UUID) -> Ingrediente:
        ...

    def salvar(self, ingrediente: Ingrediente) -> None:
        ...