"""Suíte completa de testes automatizados para a API do RocketLab.

Executável via:
    pytest tests/test_movies_api.py -v
ou:
    python tests/test_movies_api.py
"""

import math
from typing import Generator
import httpx
import pytest

BASE_URL = "http://localhost:8000/api/v1"


@pytest.fixture(scope="module")
def client() -> Generator[httpx.Client, None, None]:
    """Cliente HTTP com conexão persistente para os testes."""
    with httpx.Client(base_url=BASE_URL, timeout=15.0) as c:
        yield c


@pytest.fixture
def created_movie(client: httpx.Client) -> Generator[dict, None, None]:
    """Cria um filme completo com diretor e gêneros para uso nos testes e garante sua limpeza."""
    payload = {
        "titulo": "Pytest Fixture Movie 2026",
        "diretor": "Denis Villeneuve",
        "generos": ["Ficção científica", "Drama"],
        "ano_lancamento": 2026,
        "duracao_minutos": 155,
        "sinopse": "Filme gerado dinamicamente para testes de integração.",
    }
    response = client.post("/movies", json=payload)
    assert response.status_code == 201, f"Falha na criação da fixture: {response.text}"
    movie = response.json()

    yield movie

    # Teardown: remove o filme após o teste se ele ainda existir
    del_resp = client.delete(f"/movies/{movie['sk_movie_id']}")
    assert del_resp.status_code in (204, 404)


# =====================================================================
# 1. TESTES DE CADASTRO DE FILME (REQUISITO 1)
# =====================================================================
def test_create_movie_with_all_fields(client: httpx.Client):
    """Valida cadastro com título, diretor, gêneros, ano e sinopse."""
    payload = {
        "titulo": "Oppenheimer Special Cut",
        "diretor": "Christopher Nolan",
        "generos": ["História", "Drama"],
        "ano_lancamento": 2023,
        "duracao_minutos": 180,
        "sinopse": "A história do projeto Manhattan.",
        "url_poster": "https://image.tmdb.org/t/p/w500/test.jpg",
    }
    r = client.post("/movies", json=payload)
    assert r.status_code == 201
    data = r.json()

    assert data["titulo"] == payload["titulo"]
    assert data["diretor"] == payload["diretor"]
    assert set(data["generos"]) == set(payload["generos"])
    assert data["ano_lancamento"] == 2023
    assert data["duracao_minutos"] == 180
    assert data["sinopse"] == payload["sinopse"]
    assert data["nota_media"] is None
    assert data["total_avaliacoes"] == 0

    # Limpeza
    client.delete(f"/movies/{data['sk_movie_id']}")


def test_create_movie_validation_errors(client: httpx.Client):
    """Testa rejeição de payloads inválidos (sem título ou valores fora do padrão)."""
    # Título vazio
    r_empty = client.post("/movies", json={"titulo": ""})
    assert r_empty.status_code == 422

    # Ano inválido (ex: antes da invenção do cinema)
    r_year = client.post("/movies", json={"titulo": "Inválido", "ano_lancamento": 1500})
    assert r_year.status_code == 422

    # Duração zero ou negativa
    r_dur = client.post("/movies", json={"titulo": "Inválido", "duracao_minutos": -10})
    assert r_dur.status_code == 422


# =====================================================================
# 2. TESTES DE CATÁLOGO PAGINADO (REQUISITO 2)
# =====================================================================
def test_pagination_contract_and_structure(client: httpx.Client):
    """Valida formato dos metadados de paginação."""
    page_size = 8
    r = client.get(f"/movies?page=1&page_size={page_size}")
    assert r.status_code == 200
    data = r.json()

    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert "items" in data
    assert data["page"] == 1
    assert data["page_size"] == page_size
    assert len(data["items"]) <= page_size
    assert data["total_pages"] == math.ceil(data["total"] / page_size)


def test_pagination_disjoint_pages(client: httpx.Client):
    """Garante que a página 2 não contenha nenhum filme presente na página 1."""
    r1 = client.get("/movies?page=1&page_size=10")
    r2 = client.get("/movies?page=2&page_size=10")
    assert r1.status_code == 200 and r2.status_code == 200

    ids_p1 = {m["sk_movie_id"] for m in r1.json()["items"]}
    ids_p2 = {m["sk_movie_id"] for m in r2.json()["items"]}
    assert ids_p1.isdisjoint(ids_p2), "Itens da página 1 foram repetidos na página 2!"


def test_pagination_invalid_bounds(client: httpx.Client):
    """Verifica rejeição de parâmetros inválidos de paginação."""
    assert client.get("/movies?page=0").status_code == 422
    assert client.get("/movies?page=-1").status_code == 422
    assert client.get("/movies?page_size=0").status_code == 422
    assert client.get("/movies?page_size=101").status_code == 422  # Limite máximo é 100


# =====================================================================
# 3. TESTES DE BUSCA DE FILMES (REQUISITO 4)
# =====================================================================
def test_search_by_partial_title_and_case_insensitive(client: httpx.Client, created_movie: dict):
    """Busca por termo parcial em minúsculas deve encontrar o filme criado."""
    # Buscando por 'fixture' em minúsculas
    r = client.get("/movies?search=fixture")
    assert r.status_code == 200
    items = r.json()["items"]
    assert any(m["sk_movie_id"] == created_movie["sk_movie_id"] for m in items)


def test_search_non_existent_term(client: httpx.Client):
    """Termo sem correspondência deve retornar lista vazia e total 0."""
    r = client.get("/movies?search=TERMO_INEXISTENTE_XYZ_999999")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


# =====================================================================
# 4. TESTES DE DETALHES COMPLETOS (REQUISITO 3)
# =====================================================================
def test_get_movie_details(client: httpx.Client, created_movie: dict):
    """Consulta os detalhes completos de um filme existente."""
    movie_id = created_movie["sk_movie_id"]
    r = client.get(f"/movies/{movie_id}")
    assert r.status_code == 200
    data = r.json()

    assert data["sk_movie_id"] == movie_id
    assert data["titulo"] == created_movie["titulo"]
    assert data["diretor"] == "Denis Villeneuve"
    assert isinstance(data["genres"], list)
    assert isinstance(data["reviews"], list)


def test_get_non_existent_movie(client: httpx.Client):
    """Busca de ID que não existe deve retornar 404 Not Found."""
    r = client.get("/movies/ID_INEXISTENTE_UUID_404")
    assert r.status_code == 404
    assert r.json()["detail"] == "Filme não encontrado"


# =====================================================================
# 5. TESTES DE AVALIAÇÕES E MÉDIA ARITMÉTICA (REQUISITOS 6 E 7)
# =====================================================================
def test_review_score_boundary_conditions(client: httpx.Client, created_movie: dict):
    """Testa os limites da escala de 0 a 10 e rejeição de notas inválidas."""
    movie_id = created_movie["sk_movie_id"]

    # Limite inferior válido: 0.0
    r_zero = client.post(
        f"/movies/{movie_id}/reviews",
        json={"nome": "Ana", "nota": 0.0, "comentario": "Crítica nota zero"},
    )
    assert r_zero.status_code == 201

    # Limite superior válido: 10.0
    r_ten = client.post(
        f"/movies/{movie_id}/reviews",
        json={"nome": "Beto", "nota": 10.0, "comentario": "Obra-prima absoluta"},
    )
    assert r_ten.status_code == 201

    # Inválido: menor que 0
    assert client.post(
        f"/movies/{movie_id}/reviews",
        json={"nome": "Carlos", "nota": -0.1, "comentario": "Inválido"},
    ).status_code == 422

    # Inválido: maior que 10
    assert client.post(
        f"/movies/{movie_id}/reviews",
        json={"nome": "Daniel", "nota": 10.1, "comentario": "Inválido"},
    ).status_code == 422

    # Inválido: comentário vazio
    assert client.post(
        f"/movies/{movie_id}/reviews",
        json={"nome": "Edu", "nota": 5.0, "comentario": ""},
    ).status_code == 422

    # Inválido: nome com menos de 2 caracteres
    assert client.post(
        f"/movies/{movie_id}/reviews",
        json={"nome": "A", "nota": 5.0, "comentario": "Comentário válido"},
    ).status_code == 422

# =====================================================================
# 6. TESTES DE ATUALIZAÇÃO (PUT / PATCH) (REQUISITO 5)
# =====================================================================
def test_partial_update_patch_preserves_unmodified_fields(client: httpx.Client, created_movie: dict):
    """PATCH atualiza campos especificados e preserva os demais intactos."""
    movie_id = created_movie["sk_movie_id"]

    patch_payload = {"duracao_minutos": 200, "sinopse": "Sinopse estendida"}
    r = client.patch(f"/movies/{movie_id}", json=patch_payload)
    assert r.status_code == 200
    data = r.json()

    assert data["duracao_minutos"] == 200
    assert data["sinopse"] == "Sinopse estendida"
    # Campos que NÃO foram alterados devem permanecer iguais
    assert data["titulo"] == created_movie["titulo"]
    assert data["diretor"] == created_movie["diretor"]


def test_update_non_existent_movie(client: httpx.Client):
    """Atualização em filme inexistente deve retornar 404."""
    assert client.patch("/movies/INEXISTENTE", json={"titulo": "Novo"}).status_code == 404
    assert client.put("/movies/INEXISTENTE", json={"titulo": "Novo"}).status_code == 404


# =====================================================================
# 7. TESTES DE REMOÇÃO E INTEGRIDADE REFERENCIAL (REQUISITO 5)
# =====================================================================
def test_delete_movie_and_cascade_reviews(client: httpx.Client):
    """Remove o filme e valida que tanto ele quanto suas avaliações deixam de existir."""
    # 1. Cria um filme e uma avaliação
    m = client.post("/movies", json={"titulo": "Filme Para Deletar"}).json()
    movie_id = m["sk_movie_id"]

    client.post(f"/movies/{movie_id}/reviews", json={"nome": "User", "nota": 8.0, "comentario": "Top"})

    # 2. Deleta o filme
    del_r = client.delete(f"/movies/{movie_id}")
    assert del_r.status_code == 204

    # 3. GET subsequente deve retornar 404
    assert client.get(f"/movies/{movie_id}").status_code == 404

    # 4. DELETE repetido no mesmo ID deve retornar 404
    assert client.delete(f"/movies/{movie_id}").status_code == 404
# =====================================================================
# 8. TESTES DE média de notas (REQUISITO 7)
# =====================================================================
def test_create_movie_add_two_reviews_and_verify_average(client: httpx.Client):
    """Cria um filme, adiciona duas notas e valida se a média e o total de avaliações são calculados corretamente."""
    # 1. Cadastro do filme
    movie_payload = {
        "titulo": "Teste Média Duas Notas",
        "diretor": "Diretor Teste",
        "generos": ["Drama"],
        "ano_lancamento": 2026,
        "sinopse": "Filme para validação da média aritmética com duas avaliações.",
    }
    create_response = client.post("/movies", json=movie_payload)
    assert create_response.status_code == 201
    movie_id = create_response.json()["sk_movie_id"]

    try:
        # 2. Primeira avaliação: nota 6.0
        review_1 = {
            "nome": "Avaliador Um",
            "nota": 6.0,
            "comentario": "Primeira avaliação para teste.",
        }
        r1 = client.post(f"/movies/{movie_id}/reviews", json=review_1)
        assert r1.status_code == 201

        # 3. Segunda avaliação: nota 9.0
        review_2 = {
            "nome": "Avaliador Dois",
            "nota": 9.0,
            "comentario": "Segunda avaliação para teste.",
        }
        r2 = client.post(f"/movies/{movie_id}/reviews", json=review_2)
        assert r2.status_code == 201

        # 4. Consulta dos detalhes e verificação da média aritmética: (6.0 + 9.0) / 2 = 7.5
        detail_response = client.get(f"/movies/{movie_id}")
        assert detail_response.status_code == 200
        movie_detail = detail_response.json()

        assert movie_detail["total_avaliacoes"] == 2
        assert movie_detail["nota_media"] == 7.5
        assert len(movie_detail["reviews"]) == 2

    finally:
        # 5. Teardown: limpeza do filme de teste
        client.delete(f"/movies/{movie_id}")
# =====================================================================
# EXECUÇÃO DIRETA
# =====================================================================
if __name__ == "__main__":
    import sys

    print("\n🚀 Executando suíte de testes com pytest...\n")
    sys.exit(pytest.main(["-v", __file__]))