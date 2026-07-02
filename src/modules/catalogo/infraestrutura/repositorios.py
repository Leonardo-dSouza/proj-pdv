import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.entidades.ingrediente import Ingrediente
from src.core.excecoes import ItemNaoEncontradoError
from src.modules.catalogo.infraestrutura.mapeadores import (
    combo_para_dominio,
    ingrediente_para_dominio,
    produto_para_dominio,
)
from src.modules.catalogo.infraestrutura.modelos import ComboModel, IngredienteModel, ProdutoModel


class ProdutoRepositorySQLAlchemy:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def obter_por_id(self, produto_id: uuid.UUID):
        model = self._sessao.get(ProdutoModel, produto_id)
        if model is None:
            raise ItemNaoEncontradoError(f"Produto {produto_id} não encontrado.")
        return produto_para_dominio(model)
    
    def salvar(self, produto):
        model = ProdutoModel(nome=produto.nome, preco=produto.preco, ativo=produto.ativo)
        self._sessao.add(model)
        self._sessao.flush()
        self._sessao.commit()
        self._sessao.refresh(model)
        return produto_para_dominio(model)

    def vincular_composicao(self, produto_id: uuid.UUID, ingrediente_id: uuid.UUID, quantidade) -> None:
        from src.modules.catalogo.infraestrutura.modelos import ComposicaoItemModel

        vinculo = ComposicaoItemModel(
            produto_id=produto_id, ingrediente_id=ingrediente_id, quantidade=quantidade
        )
        self._sessao.add(vinculo)
        self._sessao.commit()


class ComboRepositorySQLAlchemy:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def obter_por_id(self, combo_id: uuid.UUID):
        model = self._sessao.get(ComboModel, combo_id)
        if model is None:
            raise ItemNaoEncontradoError(f"Combo {combo_id} não encontrado.")
        return combo_para_dominio(model)


class IngredienteRepositorySQLAlchemy:
    """Implementa o port core/interfaces/ingrediente_repository.py"""

    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def obter_para_atualizacao(self, ingrediente_id: uuid.UUID) -> Ingrediente:
        stmt = select(IngredienteModel).where(IngredienteModel.id == ingrediente_id).with_for_update()
        model = self._sessao.execute(stmt).scalar_one_or_none()
        if model is None:
            raise ItemNaoEncontradoError(f"Ingrediente {ingrediente_id} não encontrado.")
        return ingrediente_para_dominio(model)

    def salvar(self, ingrediente: Ingrediente) -> None:
        model = self._sessao.get(IngredienteModel, ingrediente.id)
        model.quantidade_estoque = ingrediente.quantidade_estoque
        self._sessao.flush()

    def salvar_novo(self, ingrediente):
        model = IngredienteModel(
            nome=ingrediente.nome,
            quantidade_estoque=ingrediente.quantidade_estoque,
            valor=ingrediente.valor,
            estoque_minimo=ingrediente.estoque_minimo,
        )
        self._sessao.add(model)
        self._sessao.flush()
        self._sessao.commit()
        self._sessao.refresh(model)
        return ingrediente_para_dominio(model)