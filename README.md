# PDV Lanchonete

Sistema de ponto de venda (PDV) para lanchonete — 100% backend, sem interface gráfica. Projeto acadêmico (FATEC São José dos Campos, Análise e Desenvolvimento de Sistemas — Fase 1: Concepção).

<p>
<a href="#escopo">Escopo</a> |
<a href="#tecnologias">Tecnologias</a> |
<a href="#requisitos">Requisitos</a> |
<a href="#arquitetura">Arquitetura</a> |
<a href="#estrutura">Estrutura</a> |
<a href="#rodar">Como rodar</a> |
<a href="#comandos">Comandos</a> |
<a href="#status">Status</a> |
<a href="#creditos">Créditos</a>
</p>

---

## 📋 Escopo

<a id="escopo"></a>

O **PDV Lanchonete** é uma API backend para operação de uma lanchonete: criação e acompanhamento de pedidos (balcão, mesa, retirada e delivery), baixa automática de estoque (incluindo composição recursiva de combos), fila de preparo para a cozinha e controle de caixa.

Não há interface gráfica — o foco do projeto é o domínio de negócio, a API e a observabilidade (logs e comportamento correto de cada endpoint), com ênfase em Clean Architecture e testes automatizados.

Fluxo âncora do sistema: **criar pedido → baixar estoque → publicar na fila → cozinha atualiza status**.

## Tecnologias

<a id="tecnologias"></a>

<div align="center">

![Python](https://img.shields.io/badge/Python-24B1B1?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-24B1B1?style=for-the-badge&logo=FASTAPI&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-24B1B1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-24B1B1?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-24B1B1?style=for-the-badge&logo=docker&logoColor=white)
![uv](https://img.shields.io/badge/uv-24B1B1?style=for-the-badge&logo=uv&logoColor=white)
![Git](https://img.shields.io/badge/Git-24B1B1?style=for-the-badge&logo=git&logoColor=white)

</div>

## Requisitos

<a id="requisitos"></a>

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) como gerenciador de dependências
- Docker + Docker Compose (para o PostgreSQL)

##  Arquitetura

<a id="arquitetura"></a>

Clean Architecture + DDD-light, com regra de dependência apontando sempre pra dentro:

```
core          → domínio puro (entidades, interfaces/ports, exceções, eventos).
                Zero dependência de FastAPI, SQLAlchemy ou qualquer infraestrutura.
modules       → um subpacote por feature (catalogo, pedidos, estoque, caixa,
                mesas, operadores), cada um dividido em aplicacao/ (casos de
                uso, services) e infraestrutura/ (models SQLAlchemy,
                repositórios, mapeadores).
infrastructure → o que é transversal a todos os módulos: engine/sessão de
                banco (database.py), segurança (security.py) e o registro
                central de models (model_registry.py).
config        → leitura de variáveis de ambiente (settings.py).
```

Padrões de projeto aplicados: **Strategy** para cálculo de preço/desconto (`Produto`/`Combo` implementando `ItemVendavel`), **Factory** para montagem de pedido conforme o tipo, e **Observer** via fila de mensageria para notificar a cozinha de forma desacoplada.

## 📦 Estrutura do Repositório

<a id="estrutura"></a>

```bash
proj-pdv/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── src/
│   ├── config/
│   │   └── settings.py
│   │
│   ├── core/
│   │   ├── entidades/       # Produto, Ingrediente, Combo, Pedido, ItemPedido, enums...
│   │   ├── interfaces/      # ports: ItemVendavel, IngredienteRepository, PublicadorEventos
│   │   ├── strategies/
│   │   ├── eventos/         # AlertaEstoque
│   │   └── excecoes/
│   │
│   ├── infrastructure/
│   │   ├── database.py      # Base, engine, SessionLocal, get_db()
│   │   ├── security.py
│   │   └── model_registry.py
│   │
│   ├── modules/
│   │   ├── catalogo/        # Produto, Ingrediente, Combo (models + repositórios)
│   │   ├── pedidos/         # CriarPedidoUseCase, models, repositórios
│   │   ├── estoque/         # EstoqueService (baixa recursiva de combo)
│   │   ├── caixa/
│   │   ├── mesas/
│   │   └── operadores/
│   │
│   ├── main.py
│   └── __init__.py
│
├── tests/
│   ├── unitarios/
│   ├── integracao/
│   └── conftest.py
│
├── .dockerignore
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── mypy.ini
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md              # Documentação principal (📍 Você está aqui!)
```

## Como rodar o projeto?

<a id="rodar"></a>

```bash
# 1. Subir o PostgreSQL
docker compose up -d postgres

# 2. Instalar dependências
uv sync

# 3. Configurar variáveis de ambiente
cp .env.example .env

# 4. Aplicar as migrations
uv run alembic upgrade head

# 5. Subir a API (reload ativo)
uv run uvicorn src.main:app --reload
```

API disponível em `http://127.0.0.1:8000`. Health check: `GET /health`.

## Comandos úteis

<a id="comandos"></a>

| Comando                                  | Descrição                              |
| ----------------------------------------- | --------------------------------------- |
| `uv run uvicorn src.main:app --reload`    | Sobe a API com reload                   |
| `uv run pytest`                           | Roda todos os testes                    |
| `uv run pytest -m smoke`                  | Roda só os testes de fumaça             |
| `uv run pytest -m unit`                   | Roda só os testes unitários (domínio)   |
| `uv run pytest -m integration`            | Roda só os testes de integração (banco) |
| `uv run mypy src`                         | Checagem de tipos (modo estrito)        |
| `uv run alembic upgrade head`             | Aplica as migrations                    |
| `uv run alembic revision -m "mensagem"`   | Cria uma nova migration                 |
| `docker compose up -d postgres`           | Sobe o banco PostgreSQL                 |

