"""
Rodar uma vez: uv run python -m src.config.seed_demo
"""
from sqlalchemy import text

from src.infrastructure.database import SessionLocal


def rodar_seed() -> None:
    sessao = SessionLocal()
    try:
        operador_id = sessao.execute(
            text(
                "INSERT INTO operadores (id, nome, email, senha, perfil) "
                "VALUES (gen_random_uuid(), 'Operador Demo', 'demo@pdv.com', 'hash', 'ATENDENTE') "
                "RETURNING id"
            )
        ).scalar_one()
        sessao.execute(
            text("INSERT INTO caixa (id, status) VALUES (gen_random_uuid(), 'ABERTO')")
        )
        sessao.commit()
        print(f"Seed ok. operador_id = {operador_id}")
    finally:
        sessao.close()


if __name__ == "__main__":
    rodar_seed()