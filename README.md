# EtiDhi Pipeline Intelligence + AI Assistant

A FastAPI application for company pipeline tracking, account ownership, partner mix and forecasts, with a read-only AI tracker assistant and document Q&A (RAG).

## Client scope delivered

- Ask the tracker in plain English; the LLM generates a constrained SQL `SELECT`, the server validates it, executes it against `companies`, and returns a grounded answer with the SQL and result rows.
- Upload partner PDF, TXT and Markdown files (8 MB default cap). Text is chunked and indexed in a persistent Chroma vector collection; document questions retrieve up to five relevant chunks and show source filenames.
- Gemini and Groq provider adapters are centralized in `llm_generate`; select one with `AI_PROVIDER`.
- API keys are read only from environment variables and must never be committed.
- AI request throttling, repeated-question caching, bounded output, safe SQL validation and source-aware "I don't know" instructions.
- AI assistant has no database write tools or routes. Existing tracker CRUD endpoints remain available to authenticated users.
- Existing registration, login, User ID recovery, password reset, password change, admin roles, analytics and responsive dashboard are retained.

## Architecture

Browser (`static/index.html`) -> FastAPI authenticated API -> provider adapter (`llm_generate`) -> Gemini or Groq.
Tracker Q&A: LLM SQL generation -> SQLGlot AST allow-list -> one bounded `SELECT` from `companies` -> answer synthesis.
Document Q&A: PDF/TXT/MD extraction -> overlapping text chunks -> Chroma persistent vector store -> top-5 retrieval -> grounded answer with filename sources.

## Local setup

Python 3.12 is recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and one provider key in `.env`.
For Gemini: `AI_PROVIDER=gemini` and `GEMINI_API_KEY=...`.
For Groq: `AI_PROVIDER=groq` and `GROQ_API_KEY=...`.

Run:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Health check: `/health`.

## Render deployment

1. Push this project to a private GitHub repository. Ensure `.env`, database files, Chroma files, and secrets are not committed.
2. In Render, create a Blueprint from `render.yaml` (or create a Python web service manually).
3. The supplied Blueprint uses Render's free web service and reuses your existing PostgreSQL database. Set `DATABASE_URL` to the existing database's internal connection string. Free web instances may sleep and their local filesystem is ephemeral; this project therefore saves extracted document chunks in PostgreSQL and rebuilds Chroma's local vector index after a restart/deploy. The first document query after a restart can be slower while embeddings are regenerated.
4. Add environment variables in Render dashboard:
   - `GEMINI_API_KEY` (or `GROQ_API_KEY`, matching `AI_PROVIDER`)
   - `ADMIN_EMAIL` and a strong `ADMIN_PASSWORD`
   - `APP_BASE_URL` = your exact deployed `https://...onrender.com` URL
   - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM` for password-reset and User-ID email delivery
5. Deploy and wait for `/health` to return `{"status":"ok"}`.
6. Register a normal user, sign out, then sign in using the configured admin email/password. Confirm role is `admin`.
7. Upload a dummy partner PDF/TXT/MD and test document Q&A. Test tracker questions such as "Which companies use KOGO?".
8. Review Render logs for startup errors. Never use real client documents or personal data in a free third-party LLM account unless the client approves that provider's data terms.

### Important deployment notes

- `SECRET_KEY` must be a long random secret. Render Blueprint generates one; never rotate it casually because it invalidates existing sessions.
- PostgreSQL is recommended for production. Local SQLite is only for development.
- Chroma uses local persistent storage at `CHROMA_PERSIST_DIR`. On Render free, its index is treated as a cache and is rebuilt from document chunks persisted in PostgreSQL. Keep `DATABASE_URL` pointed at a durable database; do not use ephemeral SQLite for production.
- The included in-memory cache and rate limiter are per-process. For multiple web instances, replace them with Redis/shared rate limiting.
- SMTP is required for actual recovery emails. If SMTP is missing, the app intentionally returns a generic success response and does not reveal reset links or User IDs.
- LLM free-tier quotas and model availability change. The app reports provider throttling rather than bypassing provider limits.
- The SQL allow-list is defence in depth; use a separate read-only database role in production as an additional control where the database provider supports it.
- Chroma's default embedding function downloads its embedding model on first use, so the first document indexing/query may be slower and requires outbound network access.

## Environment variables

See `.env.example`. Never commit `.env`, API keys, database backups, or `chroma_db/`.

## Validation

Run the safety unit tests:

```bash
python -m unittest discover -s tests -v
```

Run a syntax check:

```bash
python -m compileall app
```

## API endpoints

- `POST /api/ai/chat` — authenticated read-only tracker Q&A
- `POST /api/ai/documents` — authenticated document upload/indexing
- `POST /api/ai/ask-documents` — authenticated document Q&A
- `GET /health` — deployment health probe

The interactive API reference is available at `/docs` (disable it for public production deployments if the client requests that hardening).
