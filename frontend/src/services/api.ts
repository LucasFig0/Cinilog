import axios from 'axios';

export const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
});

export interface MovieListItem {
    sk_movie_id: string;
    id_filme: string;
    titulo: string;
    diretor?: string;
    ano_lancamento?: number;
    duracao_minutos?: number;
    url_poster?: string;
    nota_media?: number;
    total_avaliacoes: number;
    generos: string[];
}

export interface PaginatedMoviesResponse {
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
    items: MovieListItem[];
}

export interface Review {
    sk_movie_review_id: string;
    nome: string;
    nota: number;
    comentario: string;
    created_at: string;
}

export interface MovieDetail extends MovieListItem {
    data_lancamento?: string;
    status_filme?: string;
    sinopse?: string;
    url_backdrop?: string;
    reviews: Review[];
}

export interface MoviePayload {
    titulo: string;
    diretor?: string;
    generos?: string[];
    ano_lancamento?: number;
    duracao_minutos?: number;
    sinopse?: string;
    url_poster?: string;
}

export interface ReviewPayload {
    nome: string;
    nota: number;
    comentario: string;
}

export const movieService = {
    list: async (page = 1, pageSize = 18, search?: string) => {
        const params: Record<string, any> = { page, page_size: pageSize };
        if (search && search.trim()) params.search = search.trim();
        const res = await api.get<PaginatedMoviesResponse>('/movies', { params });
        return res.data;
    },

    getById: async (id: string) => {
        const res = await api.get<MovieDetail>(`/movies/${id}`);
        return res.data;
    },

    create: async (data: MoviePayload) => {
        const res = await api.post<MovieDetail>('/movies', data);
        return res.data;
    },

    update: async (id: string, data: Partial<MoviePayload>) => {
        const res = await api.patch<MovieDetail>(`/movies/${id}`, data);
        return res.data;
    },

    delete: async (id: string) => {
        await api.delete(`/movies/${id}`);
    },

    addReview: async (id: string, data: ReviewPayload) => {
        const res = await api.post<Review>(`/movies/${id}/reviews`, data);
        return res.data;
    },
};