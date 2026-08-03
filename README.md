# AI Business Intelligence Analyst

## Project Overview

Non-technical business owners and managers often can't access the data they need to make decisions. BI tools require SQL knowledge or analyst support, creating a bottleneck that slows decisions and keeps operational insights locked away from the people who need them most.

This codebase is an AI Business Intelligence Analyst that lets SMB owners and managers ask plain-English questions about their business data and get instant answers — with charts and narrative summaries — without writing a single line of SQL or waiting for a report.

Questions like *"Which customers haven't reordered in 90 days?"*, *"What were my top 5 products last quarter?"*, and *"Where are we losing margin?"* are answered in seconds, connected to a live database — no data export, no analyst required.

---

## Architecture & Solution

A text-to-SQL engine translates natural language queries into accurate, context-aware database queries using the client's schema. The LLM is provided with schema metadata, business-specific terminology, and example queries to ensure generated SQL reflects the actual data model rather than generic assumptions.

Query results are passed to a charting and narrative layer that selects the most appropriate visualisation and generates a plain-English summary alongside the raw data. Role-based access controls ensure staff only see data relevant to their function, and a query audit log provides governance visibility for administrators.

### Query Pipeline

```
User question
  → schema_inspector   — introspects live DB schema + builds context string
  → text_to_sql        — OpenAI gpt-4o translates question to safe SELECT SQL
  → query_executor     — executes SQL against PostgreSQL, returns typed rows
  → chart_selector     — picks bar / line / pie / KPI / table from result shape
  → narrator           — OpenAI gpt-4o writes a 2-3 sentence plain-English summary
  → audit_log          — records user, SQL, timing, and row count
  → Response           — { sql, chart_type, chart_data, narrative, rows }
```

---

## Key Capabilities

- Natural language to SQL translation
- Context-aware query generation from schema metadata
- Automated chart selection and generation
- Plain-English narrative summaries alongside raw results
- Live database connectivity
- Role-based data access control
- Query audit log and governance visibility
- Support for PostgreSQL and Neon (serverless Postgres)

---

## Technologies

| Layer | Technology |
|---|---|
| Backend | Python 3.9+, FastAPI, psycopg2 |
| AI | OpenAI `gpt-4o` (text-to-SQL + narrative) |
| Database | PostgreSQL / Neon Postgres |
| Frontend | React 18, TypeScript, Vite |
| Charts | Recharts |
| Auth | JWT (python-jose) |
| Deployment | Vercel (Python Serverless Functions + static frontend) |

---

## Project Structure

```
bi-analyst/
├── api/                          # Python FastAPI backend
│   ├── index.py                  # App entry point (Vercel handler via Mangum)
│   ├── routes/
│   │   ├── auth.py               # POST /api/auth/login
│   │   ├── query.py              # POST /api/query — core pipeline
│   │   └── audit.py              # GET /api/audit/logs (admin only)
│   ├── services/
│   │   ├── schema_inspector.py   # Introspects DB schema → prompt context
│   │   ├── text_to_sql.py        # NL → SQL via OpenAI
│   │   ├── query_executor.py     # Executes SQL safely, serialises results
│   │   ├── chart_selector.py     # Picks chart type from result shape
│   │   └── narrator.py           # Results → plain-English summary via OpenAI
│   ├── auth/
│   │   ├── jwt_handler.py        # Token encode/decode
│   │   └── rbac.py               # Role-based row filtering
│   ├── db/
│   │   ├── connection.py         # psycopg2 connection from DATABASE_URL
│   │   └── audit_log.py          # Writes to query_audit table
│   └── models/
│       └── schemas.py            # Pydantic request/response models
│
├── src/                          # React frontend
│   ├── App.tsx                   # Login + main shell
│   ├── components/
│   │   ├── QueryInput.tsx        # Chat-style question input + suggestion chips
│   │   ├── ResultsPanel.tsx      # Narrative + chart + data table + SQL toggle
│   │   ├── ChartRenderer.tsx     # Renders bar / line / pie / KPI from API response
│   │   └── AuditLog.tsx          # Paginated audit log (owner role only)
│   ├── hooks/
│   │   └── useQuery.ts           # POST /api/query state management
│   └── api/
│       └── client.ts             # Axios client with JWT Bearer header
│
├── seed/
│   └── seed.sql                  # SMB retailer schema + sample data
│
├── vercel.json                   # Vercel routing: /api/* → Python, /* → Vite
├── requirements.txt              # Python dependencies
├── package.json                  # Frontend dependencies
└── .env.example                  # Environment variable template
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 16 (local) or a [Neon](https://neon.tech) database
- An OpenAI API key

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd bi-analyst

pip install -r requirements.txt
npm install
```

### 2. Configure environment variables

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql:///bianalyst        # local Postgres
JWT_SECRET=your-long-random-secret
```

For Neon, replace `DATABASE_URL` with the connection string from your Neon dashboard.

### 3. Seed the database

```bash
# Local PostgreSQL
createdb bianalyst
psql bianalyst -f seed/seed.sql

# Neon
psql $DATABASE_URL -f seed/seed.sql
```

### 4. Run locally

```bash
# Terminal 1 — backend on :8000
python3 -m uvicorn api.index:app --reload --port 8000

# Terminal 2 — frontend on :5173
npm run dev
```

Or use the convenience script (starts both):

```bash
./dev.sh
```

Open **http://localhost:5173**.

---

## Demo Accounts

| Email | Password | Role | Access |
|---|---|---|---|
| owner@demo.com | demo1234 | Owner | Full data + audit log |
| manager@demo.com | demo1234 | Manager | North region only |
| staff@demo.com | demo1234 | Staff | Blocked from queries |

---

## Role-Based Access Control

Access is enforced via JWT claims. Three roles are supported:

- **Owner** — unrestricted access to all data and the audit log
- **Manager** — queries are automatically filtered to their region via a SQL CTE wrapper; no code change required from the user
- **Staff** — blocked from running ad-hoc queries at the API level

---

## Example Questions

These questions work against the included sample dataset (SMB retailer):

- *"What were my top 5 products last quarter?"*
- *"Which customers haven't reordered in 90 days?"*
- *"Where are we losing margin? Show by category."*
- *"What is total revenue by region this year?"*
- *"Show me monthly revenue for the past 6 months."*

---

## Deploying to Vercel

### 1. Provision a Neon database

In your Vercel project dashboard, add the **Neon Postgres** integration. This automatically sets the `DATABASE_URL` environment variable.

### 2. Set environment variables

In the Vercel dashboard under **Settings → Environment Variables**, add:

```
OPENAI_API_KEY=sk-...
JWT_SECRET=your-long-random-secret
```

### 3. Seed the database

```bash
vercel env pull .env.local
psql $DATABASE_URL -f seed/seed.sql
```

### 4. Deploy

```bash
vercel deploy
```

The `vercel.json` configuration routes all `/api/*` requests to the Python serverless function and serves the Vite build as a static frontend.

---

## API Reference

### `POST /api/auth/login`
```json
{ "username": "owner@demo.com", "password": "demo1234" }
```
Returns a JWT `access_token`.

### `POST /api/query`
```json
{ "question": "What were my top 5 products last quarter?" }
```
Returns:
```json
{
  "question": "...",
  "sql": "SELECT ...",
  "chart_type": "bar",
  "chart_data": [...],
  "x_key": "product_name",
  "y_keys": ["revenue"],
  "narrative": "Your top 5 products last quarter...",
  "rows": [...],
  "row_count": 5,
  "execution_ms": 13
}
```

### `GET /api/audit/logs?page=1&page_size=25`
Returns paginated query audit log. Owner role required.

---

## Business Impact

Business owners and managers gain direct access to operational insights without relying on analyst support or BI tool training. Decision-making cycles shorten as key metrics become immediately accessible. The platform surfaces trends and anomalies that had previously gone unnoticed due to the effort required to query them, enabling more proactive management of customers, products, and margins.
