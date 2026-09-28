import React, { useState } from 'react';
import { X } from 'lucide-react';
import type { MovieDetail, MoviePayload } from '../services/api';

interface MovieModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: MoviePayload) => Promise<void>;
    initialData?: MovieDetail | null;
}

export const MovieModal: React.FC<MovieModalProps> = ({
    isOpen,
    onClose,
    onSubmit,
    initialData,
}) => {
    if (!isOpen) return null;

    const [titulo, setTitulo] = useState(initialData?.titulo || '');
    const [diretor, setDiretor] = useState(initialData?.diretor || '');
    const [generosStr, setGenerosStr] = useState(initialData ? initialData.generos.join(', ') : '');
    const [ano, setAno] = useState(initialData?.ano_lancamento?.toString() || '');
    const [duracao, setDuracao] = useState(initialData?.duracao_minutos?.toString() || '');
    const [sinopse, setSinopse] = useState(initialData?.sinopse || '');
    const [urlPoster, setUrlPoster] = useState(initialData?.url_poster || '');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const payload: MoviePayload = {
                titulo,
                diretor: diretor.trim() || undefined,
                generos: generosStr.split(',').map((g) => g.trim()).filter(Boolean),
                ano_lancamento: ano ? parseInt(ano, 10) : undefined,
                duracao_minutos: duracao ? parseInt(duracao, 10) : undefined,
                sinopse: sinopse.trim() || undefined,
                url_poster: urlPoster.trim() || undefined,
            };
            await onSubmit(payload);
            onClose();
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 bg-black/75 flex items-center justify-center p-4 backdrop-blur-sm">
            <div className="bg-brand-surface border border-brand-card w-full max-w-lg rounded-lg shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                <div className="flex justify-between items-center px-6 py-4 border-b border-brand-card">
                    <h2 className="text-lg font-bold text-white">
                        {initialData ? 'Editar Filme' : 'Cadastrar Novo Filme'}
                    </h2>
                    <button onClick={onClose} className="text-brand-muted hover:text-white">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto">
                    <div>
                        <label className="block text-xs font-semibold text-brand-muted uppercase mb-1">Título *</label>
                        <input
                            required
                            value={titulo}
                            onChange={(e) => setTitulo(e.target.value)}
                            className="w-full bg-brand-dark border border-brand-card rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-accent"
                            placeholder="Ex: Oppenheimer"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-xs font-semibold text-brand-muted uppercase mb-1">Diretor</label>
                            <input
                                value={diretor}
                                onChange={(e) => setDiretor(e.target.value)}
                                className="w-full bg-brand-dark border border-brand-card rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-accent"
                                placeholder="Ex: Christopher Nolan"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-semibold text-brand-muted uppercase mb-1">Gêneros (vírgulas)</label>
                            <input
                                value={generosStr}
                                onChange={(e) => setGenerosStr(e.target.value)}
                                className="w-full bg-brand-dark border border-brand-card rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-accent"
                                placeholder="Drama, Ficção científica"
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="block text-xs font-semibold text-brand-muted uppercase mb-1">Ano de Lançamento</label>
                            <input
                                type="number"
                                value={ano}
                                onChange={(e) => setAno(e.target.value)}
                                className="w-full bg-brand-dark border border-brand-card rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-accent"
                                placeholder="Ex: 2023"
                            />
                        </div>
                        <div>
                            <label className="block text-xs font-semibold text-brand-muted uppercase mb-1">Duração (minutos)</label>
                            <input
                                type="number"
                                value={duracao}
                                onChange={(e) => setDuracao(e.target.value)}
                                className="w-full bg-brand-dark border border-brand-card rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-accent"
                                placeholder="Ex: 180"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-semibold text-brand-muted uppercase mb-1">URL do Pôster</label>
                        <input
                            value={urlPoster}
                            onChange={(e) => setUrlPoster(e.target.value)}
                            className="w-full bg-brand-dark border border-brand-card rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-accent"
                            placeholder="https://..."
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-semibold text-brand-muted uppercase mb-1">Sinopse</label>
                        <textarea
                            rows={3}
                            value={sinopse}
                            onChange={(e) => setSinopse(e.target.value)}
                            className="w-full bg-brand-dark border border-brand-card rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-accent resize-none"
                            placeholder="Descreva o enredo do filme..."
                        />
                    </div>

                    <div className="flex justify-end gap-3 pt-3 border-t border-brand-card">
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
                            {loading ? 'Salvando...' : 'Salvar Filme'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};