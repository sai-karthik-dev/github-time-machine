# GitHub Time Machine

> *"Every codebase has a story. Most teams just can't read it."*

We built GitHub Time Machine because we've all been there — staring at a legacy codebase with zero documentation, wondering why that one file has 47 commits by someone who left two years ago. Engineering knowledge gets lost in commit messages, stale wikis, and tribal memory. We wanted to fix that.

## What it does

GitHub Time Machine is an engineering intelligence dashboard. You point it at any public GitHub repo, and it builds a living map of your codebase:

- **Ask questions about the architecture** — the AI reads the actual source files, README, and commit history to answer
- **See the dependency graph** — a force-directed visual showing how files and modules connect
- **Travel through time** — a commit timeline that highlights fixes, merges, and architectural shifts
- **Find the debt** — a heatmap ranking every file by complexity, churn, and risk
- **Simulate changes** — "What happens if I refactor this file?" with blast radius analysis
- **Trace bugs to their origin** — the AI analyzes fix commits and points to the likely culprit
- **Get a refactoring plan** — based on actual commit patterns in your repo

Everything runs on real data. No mocks. No demos. You submit a GitHub URL, the pipeline clones it, parses every file with Tree-sitter, extracts functions and import edges, indexes commits, and stores it all in Supabase.

## How we built it

### The stack

| Layer | Tech | Why |
|-------|------|-----|
| Frontend | Next.js 15, React 19, Tailwind, Canvas | Fast SSR, glass-morphism UI, force-directed graph rendering |
| Backend | FastAPI | Single service handling repos, analysis, auth, and AI — no microservice complexity |
| Database | Supabase (PostgreSQL) | Real-time, RLS, serverless — perfect for a hackathon |
| AI | GPT-5.6 via OpenAI | Powers every intelligent feature |
| Deployment | Railway (backend) + Vercel (frontend) | Zero-config deploys from git pushes |

### How we used Codex + GPT-5.6

**Codex (GitHub Copilot / OpenAI Codex) was our sixth team member.** Throughout the entire hackathon, we used Codex to:

- **Scaffold the FastAPI routes** — Copilot generated the initial endpoint structure, parameter validation with Pydantic, and async patterns. We then refined each route for our specific Supabase schema.
- **Write the Tree-sitter integration** — symbol extraction for Python and JavaScript is complex. Codex handled the grammar queries while we focused on the pipeline orchestration.
- **Debug database queries** — when edge case Supabase queries failed, Copilot suggested the correct OR filters and upsert strategies.
- **Generate the Canvas force-directed graph** — the physics simulation (repulsion, attraction, gravity) was pair-programmed with Codex, iterating on damping coefficients and layout quality.
- **Handle CORS and auth edge cases** — the GitHub OAuth flow with state validation, redirect URI matching, and Supabase session exchange was built alongside Copilot suggestions.
- **Write tests and error handling** — every endpoint has fallback responses. Codex helped ensure no unhandled exceptions would crash the deployed service.

**GPT-5.6 powers the product itself:**

| Feature | GPT-5.6 Role |
|---------|-------------|
| Architect's Memory (Chat) | Grounded Q&A using real repository context — files, README, commits |
| Change Intelligence | Analyzes dependency edges and computes blast radius with risk scoring |
| Bug Origin | Reads fix commits, correlates patterns, identifies the culprit SHA |
| Refactor Planner | Studies commit history and generates actionable step-by-step plans |
| Impact Simulation | Combines graph traversal + AI analysis for "what breaks?" scenarios |

The key insight: we didn't bolt AI onto an existing tool. **The product cannot exist without GPT-5.6.** Every analysis panel that adds real value depends on the model's ability to understand code structure, infer relationships from commit messages, and generate engineering insights that a static analysis tool alone could never produce.

### Architecture

```
┌─────────────────────────────────────────┐
│             Vercel (Frontend)             │
│  Next.js 15 · glass UI · Canvas graph    │
│  Landing page · Dashboard · Auth         │
└──────────────┬──────────────────────────┘
               │  HTTPS
┌──────────────▼──────────────────────────┐
│           Railway (Backend)               │
│  FastAPI · tree-sitter · GitPython       │
│  15 endpoints · rate limiting · CORS     │
└──────────────┬──────────────────────────┘
               │  PostgreSQL
┌──────────────▼──────────────────────────┐
│           Supabase (Database)             │
│  users · repos · commits · files          │
│  edges · chat_history · analyses         │
└──────────────┬──────────────────────────┘
               │  API
┌──────────────▼──────────────────────────┐
│         OpenAI (GPT-5.6 + Codex)          │
│  chat · impact · bug_origin · refactor   │
└─────────────────────────────────────────┘
```

## Getting started

### Prerequisites

- Node.js 18+, Python 3.10+
- OpenAI API key (GPT-5.6)
- Supabase project
- GitHub OAuth App (for login)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set SUPABASE_URL, SUPABASE_SERVICE_KEY, OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

Then run `backend/database/complete_schema.sql` in the Supabase SQL Editor.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

### Live deployments

- **Backend**: `https://github-time-machine-production.up.railway.app`
- **Frontend**: `https://github-time-machine-taupe.vercel.app`

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/repositories/` | Submit a repo for analysis |
| `GET` | `/repositories/` | List analyzed repos |
| `GET` | `/repositories/{id}` | Status + metadata |
| `GET` | `/repositories/{id}/graph` | Dependency graph |
| `GET` | `/repositories/{id}/timeline` | Commit timeline |
| `GET` | `/repositories/{id}/heatmap` | Technical debt |
| `GET` | `/repositories/{id}/file_health` | Per-file health |
| `POST` | `/repositories/{id}/chat` | AI chat |
| `POST` | `/repositories/{id}/impact` | Change simulation |
| `POST` | `/repositories/{id}/bug_origin` | Bug tracker |
| `POST` | `/repositories/{id}/refactor_plan` | Refactor planner |
| `POST` | `/repos/connect` | GitHub OAuth sync |

## What makes this a strong submission

- **AI is the core, not an add-on** — remove GPT-5.6 and the product loses chat, impact analysis, bug origin, and refactor planning. Those four panels are what make the dashboard useful.
- **Codex was used throughout development** — scaffolding, debugging, optimization, edge cases. We coded alongside it, not against it.
- **It's real and working** — deployed on Railway and Vercel. Demo with any public GitHub repo. No smoke and mirrors.
- **It solves a genuine problem** — every engineer has struggled with undocumented codebases. This gives you answers, not just data.
- **Polished UX** — glass-morphism dark theme, force-directed graph, smooth animations. It feels like a product, not a proof of concept.

## Team

We built this in 48 hours for the OpenAI Build Week Hackathon.

| Name | Role | GitHub |
|------|------|--------|
| Sai Karthik | PM — architecture, AI prompt design, testing, demo | @sai-karthik-dev |
| Anmol | Frontend — components, auth, responsive design | @pvtt-anmol2 |
| Pranto | Backend — FastAPI, AI orchestration, Railway | @foysalpranto121 |
| Fernando | Backend — Git analysis, API architecture, endpoints, Vercel | @FerLpz55 |
| Vijay | Database — Supabase, schema, RLS, indexes | @vjbabu3 |
| Rachana | Frontend — UI redesign, landing page, theming | @adhikaryrachana00428-hash |

## License

MIT
