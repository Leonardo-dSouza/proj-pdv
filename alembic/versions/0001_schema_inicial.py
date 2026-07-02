"""schema inicial

Revision ID: 0001_schema_inicial
Revises:
Create Date: 2026-07-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_schema_inicial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

perfil_enum = postgresql.ENUM(
    "GERENTE",
    "ATENDENTE",
    name="perfil_enum",
    create_type=False,
)
tipo_pedido_enum = postgresql.ENUM(
    "BALCAO",
    "MESA",
    "RETIRADA",
    "DELIVERY",
    name="tipo_pedido_enum",
    create_type=False,
)
status_pedido_enum = postgresql.ENUM(
    "ABERTO",
    "PREPARO",
    "PRONTO",
    "ENTREGUE",
    "CANCELADO",
    name="status_pedido_enum",
    create_type=False,
)
mesa_status_enum = postgresql.ENUM(
    "LIVRE",
    "OCUPADA",
    "AGUARDANDO_FECHAMENTO",
    name="mesa_status_enum",
    create_type=False,
)
forma_pagamento_enum = postgresql.ENUM(
    "DINHEIRO",
    "CREDITO",
    "DEBITO",
    "PIX",
    "VOUCHER",
    name="forma_pagamento_enum",
    create_type=False,
)


def upgrade() -> None:
    perfil_enum.create(op.get_bind(), checkfirst=True)
    tipo_pedido_enum.create(op.get_bind(), checkfirst=True)
    status_pedido_enum.create(op.get_bind(), checkfirst=True)
    mesa_status_enum.create(op.get_bind(), checkfirst=True)
    forma_pagamento_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "operadores",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("senha", sa.String(), nullable=False),
        sa.Column("perfil", perfil_enum, nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("email", name="uq_operadores_email"),
    )

    op.create_table(
        "produtos",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("preco", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "ativo", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
    )

    op.create_table(
        "ingredientes",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column(
            "quantidade_estoque",
            sa.Numeric(10, 3),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("valor", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "estoque_minimo",
            sa.Numeric(10, 3),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )

    op.create_table(
        "composicao_itens",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("produto_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ingrediente_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantidade", sa.Numeric(10, 3), nullable=False),
        sa.ForeignKeyConstraint(
            ["produto_id"],
            ["produtos.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["ingrediente_id"],
            ["ingredientes.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "produto_id",
            "ingrediente_id",
            name="uq_composicao_itens_produto_ingrediente",
        ),
    )

    op.create_table(
        "combos",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column(
            "desconto",
            sa.Numeric(10, 2),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )

    op.create_table(
        "combo_produtos",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("combo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("produto_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "quantidade", sa.Integer(), server_default=sa.text("1"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["combo_id"],
            ["combos.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["produto_id"],
            ["produtos.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "combo_id",
            "produto_id",
            name="uq_combo_produtos_combo_produto",
        ),
    )

    op.create_table(
        "mesas",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            mesa_status_enum,
            server_default="LIVRE",
            nullable=False,
        ),
        sa.UniqueConstraint("numero", name="uq_mesas_numero"),
    )

    op.create_table(
        "pedidos",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("tipo", tipo_pedido_enum, nullable=False),
        sa.Column(
            "status",
            status_pedido_enum,
            server_default="ABERTO",
            nullable=False,
        ),
        sa.Column(
            "data_hora",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "valor_total",
            sa.Numeric(10, 2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "taxa_entrega",
            sa.Numeric(10, 2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("mesa_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("operador_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["mesa_id"],
            ["mesas.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["operador_id"],
            ["operadores.id"],
            ondelete="RESTRICT",
        ),
    )

    op.create_table(
        "itens_pedido",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("pedido_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("produto_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("combo_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("preco_unitario", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "desconto",
            sa.Numeric(10, 2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["pedido_id"],
            ["pedidos.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["produto_id"],
            ["produtos.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["combo_id"],
            ["combos.id"],
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "(produto_id IS NOT NULL AND combo_id IS NULL) OR "
            "(produto_id IS NULL AND combo_id IS NOT NULL)",
            name="ck_itens_pedido_item_vendavel",
        ),
    )

    op.create_table(
        "pagamentos",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("pedido_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("forma", forma_pagamento_enum, nullable=False),
        sa.Column("valor", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "data_hora",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["pedido_id"],
            ["pedidos.id"],
            ondelete="CASCADE",
        ),
    )

    op.create_table(
        "caixa",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("horario_abertura", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_abertura", sa.Date(), nullable=True),
        sa.Column("data_fechamento", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valor_abertura", sa.Numeric(10, 2), nullable=True),
        sa.Column("horario_programado", sa.Time(), nullable=True),
        sa.Column("operador_abertura_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "operador_fechamento_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["operador_abertura_id"],
            ["operadores.id"],
        ),
        sa.ForeignKeyConstraint(
            ["operador_fechamento_id"],
            ["operadores.id"],
        ),
    )


def downgrade() -> None:
    op.drop_table("caixa")
    op.drop_table("pagamentos")
    op.drop_table("itens_pedido")
    op.drop_table("pedidos")
    op.drop_table("mesas")
    op.drop_table("combo_produtos")
    op.drop_table("combos")
    op.drop_table("composicao_itens")
    op.drop_table("ingredientes")
    op.drop_table("produtos")
    op.drop_table("operadores")

    bind = op.get_bind()
    forma_pagamento_enum.drop(bind, checkfirst=True)
    mesa_status_enum.drop(bind, checkfirst=True)
    status_pedido_enum.drop(bind, checkfirst=True)
    tipo_pedido_enum.drop(bind, checkfirst=True)
    perfil_enum.drop(bind, checkfirst=True)
