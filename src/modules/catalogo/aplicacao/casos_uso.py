import uuid

from src.core.entidades.ingrediente import Ingrediente
from src.core.entidades.produto import Produto
from src.core.excecoes import IngredienteNaoEncontradoError, ProdutoNaoEncontradoError
from src.modules.catalogo.aplicacao.dtos import (
    CriarProdutoDTO,
    CriarIngredienteDTO,
    VincularComposicaoDTO,
)

class CriarProdutosUseCase:
    def __init__(self, repositorio_produtos):
        self._repositorio = repositorio_produtos

    def executar(self, dto: CriarProdutoDTO) -> Produto:
        produto = Produto(nome=dto.nome, preco=dto.preco, ativo=dto.ativo, composicao=[])
        return self._repositorio.salvar(produto)
    

class CriarIngredientesUseCase:
    def __init__(self, repositorio_ingredientes) -> None:
        self._repositorio = repositorio_ingredientes

    def executar(self, dto: CriarIngredienteDTO) -> Ingrediente:
        ingrediente = Ingrediente(
            nome=dto.nome,
            quantidade_estoque=dto.quantidade_estoque,
            valor=dto.valor,
            estoque_minimo=dto.estoque_minimo
        )
        return self._repositorio.salvar_novo(ingrediente)

class VincularComposicaoUseCase:
    def __init__(self, sessao, repositorio_produtos, repositorio_ingredientes) -> None:
        self._sessao = sessao
        self._repositorio_produtos = repositorio_produtos
        self._repositorio_ingredientes = repositorio_ingredientes

    def executar(self, dto: VincularComposicaoDTO) -> None:

        self._repositorio_produto.obter_por_id(dto.produto_id)
        try:
            self._repositorio_ingredientes.obter_para_atualizacao(dto.ingrediente_id)
        except IngredienteNaoEncontradoError:
            raise IngredienteNaoEncontradoError(f"Ingrediente com ID {dto.ingrediente_id} não encontrado.")
        
        self._repositorio_produto.vincular_composicao(
            produto_id=dto.produto_id,
            ingrediente_id=dto.ingrediente_id,
            quantidade=dto.quantidade
        )