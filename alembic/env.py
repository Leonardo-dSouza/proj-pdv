from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from src.config.settings import obter_configuracoes
from src.infrastructure.database import Base

# Conforme cada módulo for criado, importar seus modelos aqui
# (ou agregar em src/infrastructure/database.py) para o autogenerate
# do Alembic enxergar as tabelas. Exemplo:
# from src.modules.produtos.infraestrutura.modelos import ProdutoModel  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = obter_configuracoes().database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    if configuration is None:
        configuration = {}
    configuration["sqlalchemy.url"] = obter_configuracoes().database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
