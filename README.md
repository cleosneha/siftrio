# siftrio

AI Project Memory + SDLC Copilot.

A project accumulates memory over months — meetings, decisions, requirements, code — and AI reasons over that memory.

---

## Architecture

```
Workspace
  └── Clients
        └── Projects
              └── Knowledge Sources
                    ├── Meetings
                    ├── Documents
                    ├── GitHub
                    ├── Jira
                    ├── Slack
                    ├── Notion
                    └── Emails
```

All sources feed into a centralized knowledge layer — chunked, embedded, and stored in pgvector.

---

## Features

- **Workspaces & Projects** — Multi-tenant, client-bound project structure
- **Meeting Ingestion** — Upload transcripts or recordings, AI extracts requirements, decisions, action items, risks, and dependencies
- **Approval Queue** — Nothing ships automatically. Review, edit, approve, or reject before anything takes effect
- **Actions Layer** — Push approved items to GitHub Issues, Jira tickets, or roadmap
- **Project Memory** — Ask why something was built, who requested it, or what's pending. AI answers with citations from meetings and documents
- **Timeline Engine** — Auto-generated project history from discovery call to release
- **MCP Server** — Cursor/IDE integration. Query pending work, context, or decisions without leaving the editor
- **RAG Chat** — Semantic search across all project knowledge

---

## Tech Stack

| Layer      | Stack                    |
| ---------- | ------------------------ |
| API        | FastAPI (Python 3.12+)   |
| Database   | PostgreSQL 17 + pgvector |
| ORM        | SQLAlchemy 2.0 (Async)   |
| Migrations | Alembic                  |
| Validation | Pydantic                 |
| AI         | LangChain / OpenAI       |
| Embeddings | OpenAI / pgvector        |

---

## Getting Started

```bash
# Start PostgreSQL
docker compose up -d

# Copy env
cp .env.example .env

# Run migrations
alembic upgrade head

# Generate new migration (after model changes)
alembic revision --autogenerate -m "description"

# Start server
uvicorn src.main:app --reload
```

---

**Status: Under Progress**
