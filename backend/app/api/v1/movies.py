"""Endpoints REST para o catálogo de filmes e avaliações."""

import math
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.movies.models import DimGenre, DimMovie, DimPerson, DimReview, MovieReview
from app.movies.schemas import (
    MovieCreate,
    MovieDetail,
    MovieListItem,
    MovieUpdate,
    PaginatedMoviesResponse,
    ReviewCreate,
    ReviewRead,
)

router = APIRouter(prefix="/movies", tags=["Movies"])


def extract_director(people: list[DimPerson]) -> str | None:
    for p in people:
        if p.tipo_pessoa == "Diretor":
            return p.nome_pessoa
    return None


@router.get("", response_model=PaginatedMoviesResponse)
async def list_movies(
    page: int = Query(1, ge=1, description="Número da página (>= 1)"),
    page_size: int = Query(18, ge=1, le=100, description="Tamanho da página (1 a 100)"),
    search: str | None = Query(None, description="Filtro de busca por título"),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size

    # 1. Filtro seguro de busca
    conditions = []
    if search and search.strip():
        # func.lower com like garante compatibilidade total com SQLite
        term = f"%{search.strip().lower()}%"
        conditions.append(func.lower(DimMovie.titulo).like(term))

    # 2. Contagem total
    count_stmt = select(func.count(DimMovie.sk_movie_id))
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = (await db.execute(count_stmt)).scalar() or 0

    # 3. Consulta paginada com eager loading seguro das relações
    stmt = (
        select(DimMovie)
        .options(
            selectinload(DimMovie.genres),
            selectinload(DimMovie.people),
            selectinload(DimMovie.reviews_summary),
        )
        .order_by(DimMovie.ano_lancamento.desc().nulls_last())
        .offset(offset)
        .limit(page_size)
    )
    if conditions:
        stmt = stmt.where(*conditions)

    result = await db.execute(stmt)
    movies = result.scalars().all()

    items = []
    for m in movies:
        # Extração segura do diretor
        director_name = None
        if m.people:
            for p in m.people:
                if getattr(p, "tipo_pessoa", None) == "Diretor":
                    director_name = p.nome_pessoa
                    break

        # Gêneros seguros
        genre_names = [g.nome_genero for g in m.genres] if m.genres else []

        # Métricas de avaliação
        nota = None
        total_rev = 0
        if m.reviews_summary:
            nota = m.reviews_summary.nota_media_usuarios
            total_rev = m.reviews_summary.qtd_avaliacoes_usuarios or 0

        items.append(
            MovieListItem(
                sk_movie_id=m.sk_movie_id,
                id_filme=m.id_filme,
                titulo=m.titulo,
                diretor=director_name,
                ano_lancamento=m.ano_lancamento,
                duracao_minutos=m.duracao_minutos,
                url_poster=m.url_poster,
                nota_media=nota,
                total_avaliacoes=total_rev,
                generos=genre_names,
            )
        )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedMoviesResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items,
    )


@router.get("/{movie_id}", response_model=MovieDetail)
async def get_movie_detail(movie_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(DimMovie)
        .where(or_(DimMovie.sk_movie_id == movie_id, DimMovie.id_filme == movie_id))
        .options(
            selectinload(DimMovie.genres),
            selectinload(DimMovie.people),
            selectinload(DimMovie.reviews_summary),
            selectinload(DimMovie.reviews),
        )
    )
    movie = (await db.execute(stmt)).scalars().first()

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado")

    return MovieDetail(
        sk_movie_id=movie.sk_movie_id,
        id_filme=movie.id_filme,
        titulo=movie.titulo,
        diretor=extract_director(movie.people),
        data_lancamento=movie.data_lancamento,
        ano_lancamento=movie.ano_lancamento,
        duracao_minutos=movie.duracao_minutos,
        status_filme=movie.status_filme,
        sinopse=movie.sinopse,
        url_poster=movie.url_poster,
        url_backdrop=movie.url_backdrop,
        nota_media=movie.reviews_summary.nota_media_usuarios if movie.reviews_summary else None,
        total_avaliacoes=movie.reviews_summary.qtd_avaliacoes_usuarios if movie.reviews_summary else len(movie.reviews),
        generos=[g.nome_genero for g in movie.genres],
        genres=movie.genres,
        people=movie.people,
        reviews=movie.reviews,
    )


@router.post("", response_model=MovieDetail, status_code=status.HTTP_201_CREATED)
async def create_movie(payload: MovieCreate, db: AsyncSession = Depends(get_db)):
    new_movie = DimMovie(
        id_filme=f"custom-{uuid4().hex[:10]}",
        titulo=payload.titulo,
        data_lancamento=payload.data_lancamento,
        ano_lancamento=payload.ano_lancamento or (payload.data_lancamento.year if payload.data_lancamento else None),
        duracao_minutos=payload.duracao_minutos,
        status_filme=payload.status_filme,
        sinopse=payload.sinopse,
        url_poster=payload.url_poster,
        url_backdrop=payload.url_backdrop,
    )

    if payload.generos:
        for g_nome in payload.generos:
            g_stmt = select(DimGenre).where(DimGenre.nome_genero == g_nome.strip())
            genre = (await db.execute(g_stmt)).scalars().first()
            if not genre:
                genre = DimGenre(nome_genero=g_nome.strip())
                db.add(genre)
            new_movie.genres.append(genre)

    if payload.diretor:
        p_stmt = select(DimPerson).where(
            DimPerson.nome_pessoa == payload.diretor.strip(),
            DimPerson.tipo_pessoa == "Diretor",
        )
        person = (await db.execute(p_stmt)).scalars().first()
        if not person:
            person = DimPerson(nome_pessoa=payload.diretor.strip(), tipo_pessoa="Diretor")
            db.add(person)
        new_movie.people.append(person)

    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)

    return await get_movie_detail(movie_id=new_movie.sk_movie_id, db=db)


async def _apply_update(movie_id: str, payload: MovieUpdate, db: AsyncSession) -> MovieDetail:
    stmt = (
        select(DimMovie)
        .where(or_(DimMovie.sk_movie_id == movie_id, DimMovie.id_filme == movie_id))
        .options(selectinload(DimMovie.genres), selectinload(DimMovie.people))
    )
    movie = (await db.execute(stmt)).scalars().first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado")

    update_data = payload.model_dump(exclude_unset=True)

    if "generos" in update_data and update_data["generos"] is not None:
        movie.genres.clear()
        for g_nome in update_data["generos"]:
            g_stmt = select(DimGenre).where(DimGenre.nome_genero == g_nome.strip())
            genre = (await db.execute(g_stmt)).scalars().first()
            if not genre:
                genre = DimGenre(nome_genero=g_nome.strip())
                db.add(genre)
            movie.genres.append(genre)

    if "diretor" in update_data:
        movie.people = [p for p in movie.people if p.tipo_pessoa != "Diretor"]
        if update_data["diretor"]:
            d_name = update_data["diretor"].strip()
            p_stmt = select(DimPerson).where(
                DimPerson.nome_pessoa == d_name,
                DimPerson.tipo_pessoa == "Diretor",
            )
            person = (await db.execute(p_stmt)).scalars().first()
            if not person:
                person = DimPerson(nome_pessoa=d_name, tipo_pessoa="Diretor")
                db.add(person)
            movie.people.append(person)

    for field in [
        "titulo",
        "ano_lancamento",
        "data_lancamento",
        "duracao_minutos",
        "status_filme",
        "sinopse",
        "url_poster",
        "url_backdrop",
    ]:
        if field in update_data:
            setattr(movie, field, update_data[field])

    await db.commit()
    return await get_movie_detail(movie_id=movie.sk_movie_id, db=db)


@router.put("/{movie_id}", response_model=MovieDetail)
async def update_movie_put(movie_id: str, payload: MovieUpdate, db: AsyncSession = Depends(get_db)):
    return await _apply_update(movie_id, payload, db)


@router.patch("/{movie_id}", response_model=MovieDetail)
async def update_movie_patch(movie_id: str, payload: MovieUpdate, db: AsyncSession = Depends(get_db)):
    return await _apply_update(movie_id, payload, db)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(DimMovie).where(or_(DimMovie.sk_movie_id == movie_id, DimMovie.id_filme == movie_id))
    movie = (await db.execute(stmt)).scalars().first()

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado")

    await db.delete(movie)
    await db.commit()
    return None


@router.post("/{movie_id}/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def add_movie_review(movie_id: str, payload: ReviewCreate, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(DimMovie)
        .where(or_(DimMovie.sk_movie_id == movie_id, DimMovie.id_filme == movie_id))
        .options(selectinload(DimMovie.reviews_summary))
    )
    movie = (await db.execute(stmt)).scalars().first()

    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Filme não encontrado")

    new_review = MovieReview(
        sk_movie_id=movie.sk_movie_id,
        nome=payload.nome.strip(),
        nota=payload.nota,
        comentario=payload.comentario.strip(),
    )
    db.add(new_review)

    # Recálculo exato da média aritmética e contagem
    summary_stmt = select(
        func.count(MovieReview.sk_movie_review_id),
        func.sum(MovieReview.nota),
    ).where(MovieReview.sk_movie_id == movie.sk_movie_id)
    summary_res = await db.execute(summary_stmt)
    current_count, current_sum = summary_res.one()

    total_count = (current_count or 0) + 1
    total_sum = float(current_sum or 0) + payload.nota
    calculated_avg = round(total_sum / total_count, 2)

    if movie.reviews_summary:
        movie.reviews_summary.qtd_avaliacoes_usuarios = total_count
        movie.reviews_summary.nota_media_usuarios = calculated_avg
    else:
        new_summary = DimReview(
            sk_movie_id=movie.sk_movie_id,
            qtd_avaliacoes_usuarios=total_count,
            nota_media_usuarios=calculated_avg,
        )
        db.add(new_summary)

    await db.commit()
    await db.refresh(new_review)
    return new_review