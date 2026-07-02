from typing import Any, Protocol


class PublicadorEventos(Protocol):
    def publicar(self, evento: Any) -> None:
        ...