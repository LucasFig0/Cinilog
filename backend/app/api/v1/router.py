"""Ponto de composição dos routers da API v1."""

from fastapi import APIRouter
from app.api.v1.movies import router as movies_router

api_router = APIRouter()

# Registra os endpoints de filmes e avaliações
api_router.include_router(movies_router)