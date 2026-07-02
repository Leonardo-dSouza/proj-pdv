from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracoes(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    db_host: str = "localhost"
    db_port: int = 5432
    db_nome: str = "pdv"
    db_usuario: str = "pdv"
    db_senha: str = "pdv"
    ambiente: str = "development"
    jwt_secret: str = "change-me"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_usuario}:{self.db_senha}"
            f"@{self.db_host}:{self.db_port}/{self.db_nome}"
        )

    @property
    def database_url_async(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_usuario}:{self.db_senha}"
            f"@{self.db_host}:{self.db_port}/{self.db_nome}"
        )


@lru_cache
def obter_configuracoes() -> Configuracoes:
    return Configuracoes()
