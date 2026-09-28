import React, { useState } from 'react';
import { Star, X } from 'lucide-react';
import type { ReviewPayload } from '../services/api';

interface ReviewModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: ReviewPayload) => Promise<void>;
    movieTitle: string;
}

export const ReviewModal: React.FC<ReviewModalProps> = ({
    isOpen,
    onClose,
    onSubmit,
    movieTitle,
}) => {
    if (!isOpen) return null;

    const [nome, setNome] = useState('');
    const [nota, setNota] = useState(8.0);
    const [comentario, setComentario] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            await onSubmit({ nome, nota: Number(nota), comentario });
            onClose();
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 bg-black/75 flex items-center justify-center p-4 backdrop-blur-sm">
            <div className="bg-brand-surface border border-brand-card w-full max-w-md rounded-lg shadow-2xl p-6">
                <div className="flex justify-between items-center mb-4 pb-2 border-b border-brand-card">
                    <div>
                        <h3 className="text-base font-bold text-white">Avaliar Filme</h3>
                        <p className="text-xs text-brand-muted">{movieTitle}</p>
                    </div>
                    <button onClick={onClose} className="text-brand-muted hover:text-white">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-xs font-semibold text-brand-muted uppercase mb-1">Seu Nome *</label>
                        <input
                            required
                            minLength={2}
                            value={nome}
                            onChange={(e) => setNome(e.target.value)}
                            className="w-full bg-brand-dark border border-brand-card rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-accent"
                            placeholder="Ex: Seu Nome"
                        />
                    </div>

                    <div>
                        <div className="flex justify-between items-center mb-1">
                            <label className="block text-xs font-semibold text-brand-muted uppercase">Nota (0 a 10)</label>
                            <span className="text-yellow-400 font-bold flex items-center gap-1 text-sm">
                                <Star className="w-4 h-4 fill-yellow-400" />
                                {Number(nota).toFixed(1)} / 10
                            </span>
                        </div>
                        <input
                            type="range"
                            min="0"
                            max="10"
                            step="0.5"
                            value={nota}
                            onChange={(e) => setNota(parseFloat(e.target.value))}
                            className="w-full accent-brand-accent cursor-pointer"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-semibold text-brand-muted uppercase mb-1">Comentário / Resenha *</label>
                        <textarea
                            required
                            rows={4}
                            value={comentario}
                            onChange={(e) => setComentario(e.target.value)}
                            className="w-full bg-brand-dark border border-brand-card rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-accent resize-none"
                            placeholder="O que achou do filme?"
                        />
                    </div>

                    <div className="flex justify-end gap-3 pt-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 rounded text-sm text-brand-muted hover:text-white"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-5 py-2 rounded text-sm font-bold bg-brand-accent text-brand-dark hover:brightness-110 disabled:opacity-50"
                        >
                            {loading ? 'Publicando...' : 'Publicar'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};