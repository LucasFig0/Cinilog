"""Script otimizado para carregar os CSVs no banco SQLite local."""

import csv
import sqlite3
from pathlib import Path

BATCH_SIZE = 10_000


def clean_row(row: dict) -> dict:
    """Converte strings vazias ou nulas em None (NULL no SQL)."""
    cleaned = {}
    for key, value in row.items():
        if key is None:
            continue
        cleaned_key = key.strip()
        if value is None:
            cleaned[cleaned_key] = None
        else:
            val = value.strip()
            cleaned[cleaned_key] = None if val in ("", "NA", "NaN", "null") else val
    return cleaned


def seed_table(
    cursor: sqlite3.Cursor,
    csv_path: Path,
    table_name: str,
) -> int:
    """Insere registros do CSV em lotes de forma rápida e segura."""
    if not csv_path.exists():
        print(f"  Arquivo não encontrado: {csv_path.name} (ignorando)")
        return 0

    print(f" Processando {csv_path.name} -> {table_name}...", end="", flush=True)

    total_inserted = 0
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print(" vazio!")
            return 0

        columns = [col.strip() for col in reader.fieldnames if col]
        cols_quoted = [f'"{col}"' for col in columns]
        placeholders = [f":{col}" for col in columns]

        sql = f"""
            INSERT OR IGNORE INTO {table_name} ({', '.join(cols_quoted)})
            VALUES ({', '.join(placeholders)})
        """

        batch = []
        for row in reader:
            batch.append(clean_row(row))
            if len(batch) >= BATCH_SIZE:
                cursor.executemany(sql, batch)
                total_inserted += len(batch)
                batch.clear()

        if batch:
            cursor.executemany(sql, batch)
            total_inserted += len(batch)

    print(f" Concluído! ({total_inserted} registros)")
    return total_inserted


def main():
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "rocketlab.db"
    data_dir = base_dir / "data"

    if not db_path.exists():
        print(f" Banco {db_path} não encontrado! Execute 'alembic upgrade head' primeiro.")
        return

    print(f"  Banco de dados: {db_path.resolve()}")
    print(f" Diretório de dados: {data_dir.resolve()}\n")

    conn = sqlite3.connect(db_path)
    # Desativa foreign keys durante carga em massa para ganho de performance e integridade
    conn.execute("PRAGMA synchronous = OFF;")
    conn.execute("PRAGMA journal_mode = MEMORY;")
    conn.execute("PRAGMA foreign_keys = OFF;")
    cursor = conn.cursor()

    try:
        # 1. Dimensões base
        print("--- [1/4] Dimensões Base ---")
        seed_table(cursor, data_dir / "dim_genres.csv", "dim_genres")
        seed_table(cursor, data_dir / "dim_companies.csv", "dim_companies")
        seed_table(cursor, data_dir / "dim_people.csv", "dim_people")
        seed_table(cursor, data_dir / "dim_movies.csv", "dim_movies")

        # 2. Tabelas associativas
        print("\n--- [2/4] Tabelas Associativas (Bridges) ---")
        seed_table(cursor, data_dir / "bridge_movie_genre.csv", "bridge_movie_genre")
        seed_table(cursor, data_dir / "bridge_movie_company.csv", "bridge_movie_company")
        seed_table(cursor, data_dir / "bridge_movie_person.csv", "bridge_movie_person")

        # 3. Fatos e Resumo
        print("\n--- [3/4] Fatos e Desempenho ---")
        seed_table(cursor, data_dir / "fact_movies_performance.csv", "fact_movies_performance")
        seed_table(cursor, data_dir / "dim_reviews.csv", "dim_reviews")

        # 4. Reviews
        print("\n--- [4/4] Avaliações Individuais ---")
        reviews_csv = (
            data_dir / "movies_reviews.csv"
            if (data_dir / "movies_reviews.csv").exists()
            else data_dir / "movie_reviews.csv"
        )
        seed_table(cursor, reviews_csv, "movie_reviews")

        conn.commit()
        print("\n Todas as tabelas foram carregadas com sucesso!")

    except Exception as e:
        conn.rollback()
        print(f"\n Erro durante o seed: {e}")
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    main()