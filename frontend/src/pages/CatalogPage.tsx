import React, { useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { MovieCard } from '../components/MovieCard';
import { MovieModal } from '../components/MovieModal';
import { Navbar } from '../components/Navbar';
import { movieService, type MovieListItem, type MoviePayload } from '../services/api';

export const CatalogPage: React.FC = () => {
    const [searchParams] = useSearchParams();
    const search = searchParams.get('search') || '';

    const [movies, setMovies] = useState<MovieListItem[]>([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [isCreateOpen, setIsCreateOpen] = useState(false);

    const fetchMovies = async () => {
        setLoading(true);
        try {
            const data = await movieService.list(page, 18, search);
            setMovies(data.items);
            setTotalPages(data.total_pages);
            setTotal(data.total);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        setPage(1);
    }, [search]);

    useEffect(() => {
        fetchMovies();
    }, [page, search]);

    const handleCreateMovie = async (data: MoviePayload) => {
        await movieService.create(data);
        fetchMovies();
    };

    return (
        <div className="min-h-screen bg-brand-dark flex flex-col">
            <Navbar onOpenCreate={() => setIsCreateOpen(true)} initialSearch={search} />

            <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-2xl font-black text-white">
                            {search ? `Resultados para "${search}"` : 'Catálogo de Filmes'}
                        </h1>
                        <p className="text-sm text-brand-muted mt-1">
                            {total.toLocaleString()} filmes encontrados
                        </p>
                    </div>
                </div>

                {loading ? (
                    <div className="flex flex-col items-center justify-center py-32 text-brand-muted">
                        <Loader2 className="w-10 h-10 animate-spin text-brand-accent mb-3" />
                        <p className="text-sm">Carregando catálogo...</p>
                    </div>
                ) : movies.length === 0 ? (
                    <div className="text-center py-24 bg-brand-surface/40 rounded-lg border border-brand-card">
                        <p className="text-brand-muted text-base">Nenhum filme encontrado para essa busca.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        {movies.map((movie) => (
                            <MovieCard key={movie.sk_movie_id} movie={movie} />
                        ))}
                    </div>
                )}

                {totalPages > 1 && (
                    <div className="flex justify-center items-center gap-3 mt-10">
                        <button
                            onClick={() => setPage((p) => Math.max(p - 1, 1))}
                            disabled={page === 1 || loading}
                            className="flex items-center gap-1 px-3 py-1.5 rounded bg-brand-surface border border-brand-card text-sm text-white hover:border-brand-accent disabled:opacity-40"
                        >
                            <ChevronLeft className="w-4 h-4" /> Anterior
                        </button>

                        <span className="text-sm text-brand-muted px-2">
                            Página <strong className="text-white">{page}</strong> de <strong className="text-white">{totalPages}</strong>
                        </span>

                        <button
                            onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                            disabled={page === totalPages || loading}
                            className="flex items-center gap-1 px-3 py-1.5 rounded bg-brand-surface border border-brand-card text-sm text-white hover:border-brand-accent disabled:opacity-40"
                        >
                            Próxima <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                )}
            </main>

            <MovieModal
                isOpen={isCreateOpen}
                onClose={() => setIsCreateOpen(false)}
                onSubmit={handleCreateMovie}
            />
        </div>
    );
};