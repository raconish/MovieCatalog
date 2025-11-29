# Movie Catalog – Projeto Integrador I

Aplicação web full stack para catálogo de filmes, desenvolvida com **FastAPI**, **SQLAlchemy**, **PostgreSQL** e **Jinja2**.

## Objetivo

Demonstrar:

- CRUD completo (Create, Read, Update, Delete) de filmes
- API RESTful robusta e bem estruturada
- Separação de camadas no back-end
- Modelagem relacional com PostgreSQL
- Interface web funcional consumindo o back-end

---

## Arquitetura (Camadas)

- `database.py`  
  - Configuração do banco (PostgreSQL)
  - `engine`, `SessionLocal`, `Base`

- `models.py`  
  - Mapeamento objeto-relacional (ORM) das entidades:
    - `User`, `Director`, `Genre`, `Movie`, `Review`, `Show`
  - Relacionamentos:
    - `Movie` ↔ `Genre` (N:N com tabela associativa)
    - `Director` ↔ `Movie`
    - `Movie` ↔ `Review`

- `crud.py`  
  - Camada de regras de negócio / acesso a dados:
    - Funções de CRUD para filmes
    - Funções auxiliares para diretores e gêneros
    - Versões baseadas em IDs (API) e baseadas em nomes (HTML)

- `main.py`  
  - Controlador (FastAPI):
    - Rotas HTML (server-side rendering)
    - Rotas API REST (`/api/movies`)
    - Autenticação simples (login/logout via cookie)

- `templates/`  
  - Páginas Jinja2:
    - `index.html`, `add_movie.html`, `edit_movie.html`, `delete_movie.html`
    - `movie_modal.html` (detalhes via modal)
    - `login.html`

- `static/style.css`  
  - Estilos visuais da interface

---

## API RESTful

Endpoints principais (JSON):

- `GET /api/movies`  
  Retorna lista de filmes.

- `GET /api/movies/{id}`  
  Retorna detalhes de um filme.

- `POST /api/movies`  
  Cria um filme.

  Exemplo de corpo (JSON):

  ```json
  {
    "title": "Inception",
    "year": 2010,
    "description": "A thief who steals corporate secrets...",
    "director_id": 1,
    "genre_ids": [1, 2],
    "image_url": "https://example.com/poster.jpg"
  }
