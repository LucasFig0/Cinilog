import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { CatalogPage } from './pages/CatalogPage';
import { MovieDetailPage } from './pages/MovieDetailPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CatalogPage />} />
        <Route path="/movies/:id" element={<MovieDetailPage />} />
      </Routes>
    </BrowserRouter>
  );
}