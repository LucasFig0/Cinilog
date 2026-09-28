import React, { useState } from 'react';
import { Film, Plus, Search } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

interface NavbarProps {
    onOpenCreate?: () => void;
    initialSearch?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenCreate, initialSearch = '' }) => {
    const [term, setTerm] = useState(initialSearch);
    const navigate = useNavigate();

    const handleSearchSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (term.trim()) {
            navigate(`/?search=${encodeURIComponent(term.trim())}`);
        } else {
            navigate('/');
        }
    };

    return (
        <nav className="bg-brand-surface border-b border-brand-card sticky top-0 z-40 backdrop-blur-md">
            <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
                <Link to="/" className="flex items-center gap-2 text-xl font-black tracking-wider text-white hover:opacity-90">
                    <Film className="text-brand-accent w-7 h-7" />
                    <span>ROCKET<span className="text-brand-accent">LAB</span></span>
                </Link>

                <form onSubmit={handleSearchSubmit} className="flex-1 max-w-md relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-brand-muted" />
                    <input
                        type="text"
                        value={term}
                        onChange={(e) => setTerm(e.target.value)}
                        placeholder="Buscar filmes por título..."
                        className="w-full bg-brand-dark/80 border border-brand-card rounded-full pl-9 pr-4 py-1.5 text-sm text-white placeholder-brand-muted focus:outline-none focus:border-brand-accent transition-colors"
                    />
                </form>

                {onOpenCreate && (
                    <button
                        onClick={onOpenCreate}
                        className="flex items-center gap-1.5 bg-brand-accent text-brand-dark font-bold text-xs uppercase px-4 py-2 rounded-md hover:brightness-110 active:scale-95 transition-all shadow-md"
                    >
                        <Plus className="w-4 h-4 stroke-[3]" />
                        Novo Filme
                    </button>
                )}
            </div>
        </nav>
    );
};