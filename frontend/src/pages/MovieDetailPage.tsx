import React, { useEffect, useState } from 'react';
import { ArrowLeft, Edit, MessageSquare, Star, Trash2 } from 'lucide-react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { MovieModal } from '../components/MovieModal';
import { Navbar } from '../components/Navbar';
import { ReviewModal } from '../components/ReviewModal';
import { type MovieDetail, type MoviePayload, type ReviewPayload, movieService } from '../services/api';

export const MovieDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    const [movie, setMovie] = useState<MovieDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [isEditOpen, setIsEditOpen] = useState(false);
    const [isReviewOpen, setIsReviewOpen] = useState(false);

    const fetchDetail = async () => {
        if (!id) return;
        setLoading(true);
        try {
            const data = await movieService.getById(id);
            setMovie(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDetail();
    }, [id]);

    const handleUpdate = async (data: MoviePayload) => {
        if (!id) return;
        await movieService.update(id, data);
        fetchDetail();
    };

    const handleDelete = async () => {
        if (!id || !movie) return;
        if (window.confirm(`Tem certeza que deseja excluir "${movie.titulo}"?`)) {
            await movieService.delete(id);
            navigate('/');
        }
    };

    const handleAddReview = async (data: ReviewPayload) => {
        if (!id) return;
        await movieService.addReview(id, data);
        fetchDetail();
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-brand-dark flex items-center justify-center text-white">
                Carregando detalhes...
            </div>
        );
    }

    if (!movie) {
        return (
            <div className="min-h-screen bg-brand-dark flex flex-col items-center justify-center text-white gap-4">
                <p>Filme não encontrado.</p>
                <Link to="/" className="text-brand-accent hover:underline">Voltar ao catálogo</Link>
            </div>
        );
    }

    const posterUrl = movie.url_poster?.startsWith('http')
        ? movie.url_poster
        : movie.url_poster
            ? `https://image.tmdb.org/t/p/w500${movie.url_poster}`
            : 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&q=80';

    return (
        <div className="min-h-screen bg-brand-dark flex flex-col">
            <Navbar />

            <main className="flex-1 max-w-5xl w-full mx-auto px-4 py-8">
                <Link to="/" className="inline-flex items-center gap-1.5 text-xs text-brand-muted hover:text-white mb-6 uppercase tracking-wider font-semibold">
                    <ArrowLeft className="w-4 h-4" /> Voltar ao Catálogo
                </Link>

                <div className="flex flex-col md:flex-row gap-8 bg-brand-surface/60 border border-brand-card p-6 rounded-lg shadow-xl">
                    <div className="w-48 sm:w-56 shrink-0 aspect-[2/3] rounded overflow-hidden shadow-lg border border-brand-card">
                        <img src={posterUrl} alt={movie.titulo} className="w-full h-full object-cover" />
                    </div>

                    <div className="flex-1 flex flex-col justify-between">
                        <div>
                            <div className="flex justify-between items-start gap-4">
                                <h1 className="text-3xl font-black text-white">{movie.titulo}</h1>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => setIsEditOpen(true)}
                                        className="p-2 rounded bg-brand-card hover:bg-brand-surface text-brand-muted hover:text-white border border-brand-card"
                                        title="Editar Filme"
                                    >
                                        <Edit className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={handleDelete}
                                        className="p-2 rounded bg-brand-card hover:bg-red-500/20 text-brand-muted hover:text-red-400 border border-brand-card"
                                        title="Excluir Filme"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <p className="text-sm text-brand-muted mt-1">
                                {movie.ano_lancamento || 'Ano N/A'} • {movie.duracao_minutos ? `${movie.duracao_minutos} min` : 'Duração N/A'}
                                {movie.diretor && <span> • Dirigido por <strong className="text-white">{movie.diretor}</strong></span>}
                            </p>

                            <div className="flex flex-wrap gap-2 my-4">
                                {movie.generos.map((g) => (
                                    <span key={g} className="text-xs bg-brand-card text-brand-muted px-2.5 py-1 rounded-full border border-brand-card">
                                        {g}
                                    </span>
                                ))}
                            </div>

                            <div className="flex items-center gap-6 py-4 my-2 border-y border-brand-card">
                                <div className="flex items-center gap-2">
                                    <Star className="w-7 h-7 fill-yellow-400 text-yellow-400" />
                                    <div>
                                        <div className="text-2xl font-black text-white leading-none">
                                            {movie.nota_media !== null && movie.nota_media !== undefined ? movie.nota_media.toFixed(1) : '—'}
                                            <span className="text-xs text-brand-muted font-normal"> / 10</span>
                                        </div>
                                        <span className="text-[11px] text-brand-muted">Média Geral</span>
                                    </div>
                                </div>

                                <div className="border-l border-brand-card pl-6">
                                    <div className="text-2xl font-black text-white leading-none">
                                        {movie.total_avaliacoes}
                                    </div>
                                    <span className="text-[11px] text-brand-muted">Avaliações Totais</span>
                                </div>

                                <button
                                    onClick={() => setIsReviewOpen(true)}
                                    className="ml-auto flex items-center gap-2 bg-brand-accent text-brand-dark px-4 py-2 rounded font-bold text-xs uppercase hover:brightness-110 shadow-md"
                                >
                                    <MessageSquare className="w-4 h-4" />
                                    Avaliar
                                </button>
                            </div>

                            <div className="mt-4">
                                <h3 className="text-xs font-bold uppercase tracking-wider text-brand-muted mb-1">Sinopse</h3>
                                <p className="text-sm text-gray-300 leading-relaxed">
                                    {movie.sinopse || 'Nenhuma sinopse disponível para este filme.'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mt-10">
                    <h2 className="text-xl font-bold text-white mb-4">
                        Resenhas dos Usuários ({movie.reviews.length})
                    </h2>

                    {movie.reviews.length === 0 ? (
                        <div className="bg-brand-surface/40 border border-brand-card rounded-lg p-6 text-center text-brand-muted text-sm">
                            Nenhuma resenha registrada ainda. Seja o primeiro a avaliar!
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {movie.reviews.map((rev) => (
                                <div key={rev.sk_movie_review_id} className="bg-brand-surface border border-brand-card p-4 rounded-lg">
                                    <div className="flex justify-between items-center mb-2">
                                        <div className="flex items-center gap-2">
                                            <span className="font-bold text-sm text-white">{rev.nome}</span>
                                            <span className="text-xs text-brand-muted">
                                                • {new Date(rev.created_at).toLocaleDateString('pt-BR')}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-1 text-yellow-400 font-bold text-xs bg-brand-dark px-2 py-0.5 rounded border border-brand-card">
                                            <Star className="w-3 h-3 fill-yellow-400" />
                                            {rev.nota.toFixed(1)}
                                        </div>
                                    </div>
                                    <p className="text-sm text-gray-300 leading-relaxed">{rev.comentario}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </main>

            <MovieModal
                isOpen={isEditOpen}
                onClose={() => setIsEditOpen(false)}
                onSubmit={handleUpdate}
                initialData={movie}
            />

            <ReviewModal
                isOpen={isReviewOpen}
                onClose={() => setIsReviewOpen(false)}
                onSubmit={handleAddReview}
                movieTitle={movie.titulo}
            />
        </div>
    );
};