import React from 'react';
import { Star } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { MovieListItem } from '../services/api';

interface MovieCardProps {
    movie: MovieListItem;
}

export const MovieCard: React.FC<MovieCardProps> = ({ movie }) => {
    const posterUrl = movie.url_poster?.startsWith('http')
        ? movie.url_poster
        : movie.url_poster
            ? `https://image.tmdb.org/t/p/w500${movie.url_poster}`
            : 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&q=80';

    return (
        <Link
            to={`/movies/${movie.sk_movie_id}`}
            className="group bg-brand-surface rounded-md overflow-hidden border border-brand-card hover:border-brand-accent transition-all duration-200 flex flex-col hover:-translate-y-1 shadow-md"
        >
            <div className="relative aspect-[2/3] w-full overflow-hidden bg-brand-card">
                <img
                    src={posterUrl}
                    alt={movie.titulo}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                />
                {movie.nota_media !== null && movie.nota_media !== undefined && (
                    <div className="absolute top-2 right-2 bg-brand-dark/85 backdrop-blur-sm px-2 py-0.5 rounded text-xs font-bold text-yellow-400 flex items-center gap-1 border border-yellow-500/20">
                        <Star className="w-3 h-3 fill-yellow-400" />
                        <span>{movie.nota_media.toFixed(1)}</span>
                    </div>
                )}
            </div>

            <div className="p-3 flex-1 flex flex-col justify-between">
                <div>
                    <h3 className="font-bold text-sm text-white line-clamp-1 group-hover:text-brand-accent transition-colors">
                        {movie.titulo}
                    </h3>
                    <p className="text-xs text-brand-muted mt-1">
                        {movie.ano_lancamento || 'S/D'} {movie.diretor ? `• ${movie.diretor}` : ''}
                    </p>
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                    {movie.generos.slice(0, 2).map((g) => (
                        <span key={g} className="text-[10px] bg-brand-dark/60 text-brand-muted px-1.5 py-0.5 rounded border border-brand-card">
                            {g}
                        </span>
                    ))}
                </div>
            </div>
        </Link>
    );
};