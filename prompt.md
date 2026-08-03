# Prompt: Illustrative Codebase from a Case Study PDF

Use this prompt to instruct a coding agent to build a working codebase from a project case study document.

---

> I have a project case study PDF at `[path/to/file.pdf]`. Build an illustrative codebase that brings this case study to life as working, runnable code.
>
> Requirements:
> - The codebase should demonstrate every key capability listed in the PDF with real, functional code — not stubs or placeholders
> - Match the technology stack described in the PDF as closely as possible
> - Deploy target: Vercel monorepo (Python serverless functions for the backend, React/Vite for the frontend, Neon Postgres for the database)
> - Include realistic sample data that lets someone exercise the core features immediately after setup
> - Include a README that mirrors the language and structure of the PDF, extended with setup instructions, project structure, and API reference
> - The code should be illustrative but production-minded: proper separation of concerns, role-based access, error handling at system boundaries, and an audit trail where relevant
>
> Before building, share your approach for my approval.

---

## Why each instruction matters

| Phrase | Why it matters |
|---|---|
| "every key capability… with real functional code" | Prevents stub implementations |
| "realistic sample data" | Forces the agent to think through the domain and make the features actually testable |
| "mirrors the language and structure of the PDF" | Keeps the README aligned with the source document |
| "production-minded" | Pushes toward RBAC, audit logs, error handling — not just a happy-path demo |
| "share your approach for my approval" | Triggers plan mode so you can steer before any code is written |
