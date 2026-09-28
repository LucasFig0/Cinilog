"""Esquemas Pydantic para validação e serialização do domínio de filmes."""

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# --- Avaliações (Escala 0 a 10) ---
class ReviewCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120, description="Nome do usuário")
    nota: float = Field(..., ge=0.0, le=10.0, description="Nota na escala de 0 a 10")
    comentario: str = Field(..., min_length=1, max_length=4000, description="Resenha em texto")


class ReviewRead(BaseModel):
    sk_movie_review_id: str
    nome: str
    nota: float
    comentario: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Entidades Relacionadas ---
class GenreRead(BaseModel):
    sk_genre_id: str
    nome_genero: str

    model_config = ConfigDict(from_attributes=True)


class PersonRead(BaseModel):
    sk_person_id: str
    nome_pessoa: str
    tipo_pessoa: str

    model_config = ConfigDict(from_attributes=True)


# --- Filmes ---
class MovieCreate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=500)
    diretor: Optional[str] = Field(None, max_length=255, description="Nome do diretor")
    generos: List[str] = Field(default_factory=list, description="Lista com nomes dos gêneros")
    ano_lancamento: Optional[int] = Field(None, ge=1888, le=2100)
    data_lancamento: Optional[date] = None
    duracao_minutos: Optional[int] = Field(None, ge=1)
    status_filme: Optional[str] = "Released"
    sinopse: Optional[str] = None
    url_poster: Optional[str] = None
    url_backdrop: Optional[str] = None


class MovieUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=500)
    diretor: Optional[str] = Field(None, max_length=255)
    generos: Optional[List[str]] = None
    ano_lancamento: Optional[int] = None
    data_lancamento: Optional[date] = None
    duracao_minutos: Optional[int] = None
    status_filme: Optional[str] = None
    sinopse: Optional[str] = None
    url_poster: Optional[str] = None
    url_backdrop: Optional[str] = None


class MovieListItem(BaseModel):
    sk_movie_id: str
    id_filme: str
    titulo: str
    diretor: Optional[str] = None
    ano_lancamento: Optional[int] = None
    duracao_minutos: Optional[int] = None
    url_poster: Optional[str] = None
    nota_media: Optional[float] = None
    total_avaliacoes: int = 0
    generos: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class MovieDetail(MovieListItem):
    data_lancamento: Optional[date] = None
    status_filme: Optional[str] = None
    sinopse: Optional[str] = None
    url_backdrop: Optional[str] = None
    genres: List[GenreRead] = []
    people: List[PersonRead] = []
    reviews: List[ReviewRead] = []


class PaginatedMoviesResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[MovieListItem]