# Cinilog (RocketLab Movies)

Sistema full-stack para catalogação, exploração analítica e avaliação de obras cinematográficas. O projeto combina uma API assíncrona orientada a domínios relacionais com uma interface moderna para consumo de metadados, controle de notas e gestão de resenhas.

---

## 1. Visão Geral da Arquitetura

O sistema é dividido em duas camadas isoladas:

* **Backend**: Desenvolvido em Python com FastAPI, estruturado com SQLAlchemy assíncrono para manipulação relacional e validação rigorosa de esquemas via Pydantic v2.
* **Frontend**: Aplicação em camada única (SPA) desenvolvida em React com TypeScript, empacotada via Vite e estilizada com Tailwind CSS, integrando rotas dinâmicas e clientes de serviço tipados.

---

## 2. Tecnologias Utilizadas

### Backend
* Python 3.12+
* FastAPI
* Uvicorn (servidor ASGI)
* SQLAlchemy 2.0 (modo assíncrono)
* SQLite / aiosqlite
* Pydantic v2
* Pytest e HTTPX (suíte de testes assíncronos)

### Frontend
* React 18+
* TypeScript
* Vite
* Tailwind CSS
* PostCSS / Autoprefixer
* Axios
* React Router DOM
* Lucide React

---

## 3. Modelo de Dados e Regras de Negócio

O esquema de banco de dados e as validações da camada de transporte asseguram integridade estrita:

* **Escala de Avaliação**: O sistema aceita pontuações de 0.0 a 10.0, com validação no modelo Pydantic e restrições de integridade no banco.
* **Agregação Dinâmica**: A média geral e o total de avaliações são atualizados de forma consistente a cada nova submissão.
* **Relacionamentos Dimensionais**: Títulos cinematográficos estão associados de forma desacoplada a pessoas (como diretores) e múltiplos gêneros textuais.
* **Exclusão em Cascata**: A remoção de um filme remove em cascata todas as avaliações e associações dependentes.
* **Eager Loading e Paginação**: A listagem de filmes emprega paginação por limites e deslocamentos (offset), com carregamento preventivo (selectinload) de relacionamentos para evitar o problema de consultas N+1.

---

## 4. Estrutura de Diretórios

```text
Rocket_filme6/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       └── movies.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── db/
│   │   │   └── session.py
│   │   ├── models/
│   │   │   └── movie.py
│   │   ├── schemas/
│   │   │   └── movie.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_flow.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MovieCard.tsx
│   │   │   ├── MovieModal.tsx
│   │   │   ├── Navbar.tsx
│   │   │   └── ReviewModal.tsx
│   │   ├── pages/
│   │   │   ├── CatalogPage.tsx
│   │   │   └── MovieDetailPage.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
```
## 5. Endpoints da API

* **GET /api/v1/movies**: Listagem paginada com suporte aos parâmetros de consulta page, page_size e search.
* **POST /api/v1/movies**: Cadastro de novo filme contendo dados técnicos, diretores e lista de géneros.
* **GET /api/v1/movies/{id}**: Recuperação de detalhes completos do filme e resenhas associadas.
* **PATCH /api/v1/movies/{id}**: Atualização parcial dos atributos de uma obra cadastrada.
* **DELETE /api/v1/movies/{id}**: Remoção física do filme com exclusão em cascata das avaliações vinculadas.
* **POST /api/v1/movies/{id}/reviews**: Registo de resenha com cálculo automático da nova média aritmética.
* **GET /health**: Verificação da disponibilidade operacional do serviço.

---

## 6. Configuração e Instalação

### Pré-requisitos
* Git
* Python 3.12 ou superior
* Node.js 18 ou superior com gestor npm
### Configuração do Backend

1. Acessar o diretório do backend:
```bash
cd backend
```

2. Criar e ativar o ambiente virtual:
* No Windows:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
* No Linux ou macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instalar as dependências:
```bash
pip install -r requirements.txt
```

4. Executar o servidor Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```

A API responde no endereço `http://localhost:8000` e a documentação interativa Swagger fica disponível em `http://localhost:8000/docs`.

### Configuração do Frontend

1. Abrir um novo terminal e acessar o diretório do frontend:
```bash
cd frontend
```

2. Instalar as dependências:
```bash
npm install
```

3. Iniciar o servidor de desenvolvimento:
```bash
npm run dev
```

A aplicação visual fica disponível para acesso no navegador no endereço `http://localhost:5173`.

---

## 7. Execução dos Testes Automatizados

A camada de testes valida regras de negócio com o framework Pytest e requisições assíncronas via cliente HTTPX:

* **Validação Numérica**: Garantia de rejeição para notas fora do intervalo fechado de 0.0 a 10.0.
* **Integridade de Paginação**: Verificação de limites, deslocamento e integridade dos conjuntos de dados retornados em páginas sequenciais.
* **Busca Textual**: Validação de consultas por substrings e insensibilidade a maiúsculas ou minúsculas.
* **Integridade Referencial**: Confirmação da remoção em cascata de resenhas associadas quando o filme correspondente é deletado.
* **Consistência Estatística**: Verificação do recálculo exato da média aritmética e do contador total de avaliações após inserções.
   
