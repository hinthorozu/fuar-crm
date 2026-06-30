# MASTER_CONTEXT

## Product

FAIR CRM is a web-based CRM product for fair/exhibition customer management.
The target is not only infrastructure but a usable commercial product.

## Version Roadmap

- v0.0 — Foundation
- v0.1 — Usable CRM
- v0.2 — Smart Import Engine
- v0.3 — Scraper Framework
- v1.0 — First commercial release

## Permanent Rules

- Backend/database/API naming must be English.
- Frontend labels and user-facing messages must be Turkish.
- Preserve the current architecture unless there is a strong reason to change it.
- Do not propose large architecture changes before using the existing structure.
- Keep project information centralized in `FAIR_CRM_PROJECT.xlsx`.
- Keep only essential root Markdown files: `README.md`, `MASTER_CONTEXT.md`, `CHANGELOG.md`.
- Real credentials must never be hardcoded or committed.
- Local database credentials must live in `backend/.env`.
- `backend/.env.example` is the committed safe template.

## Current Architecture

- Backend: FastAPI
- ORM: SQLAlchemy
- Database: MySQL/MariaDB through PyMySQL
- Frontend target: React / TypeScript
- Project hub: `FAIR_CRM_PROJECT.xlsx`

## Import Direction

The import system must support:

- Import Preview
- Duplicate Detection
- Merge Decision
- Turkish character normalization
- Legal suffix normalization/removal
- Fuzzy company matching

## Current Product Rule

We are no longer only building infrastructure. Every change should help FAIR CRM become a usable CRM product.


## Local Verification Standard

Every development package should include and preserve `scripts/health_check.py`.
After configuration, database initialization and seed loading, run:

```bash
python scripts/health_check.py
```

The health check is the local readiness gate for FAIR CRM. It verifies environment variables, database connectivity, required tables, seed counts, FastAPI importability, key routes and the Excel project hub.


---

# Development Rules

- GitHub `main` is the single source of truth.
- Do not introduce major architectural changes; improve the existing structure.
- Every completed feature must pass:
  - `python scripts/dev_check.py`
  - `python scripts/health_check.py`
- Keep backend naming in English and frontend labels in Turkish.
- Update CHANGELOG.md and FAIR_CRM_PROJECT.xlsx after each completed feature.

# High-Level Roadmap

1. Authentication & Users
2. Customer Management
3. Fair & Participation Management
4. Excel Import Engine
5. Duplicate Detection & Merge
6. Scraper Framework
7. Dashboard & Reports
8. Communication (WhatsApp / Email)
9. Production Hardening


## Authentication & SaaS Design Rules
- FAIR CRM is designed as a future SaaS product.
- Backend/database/API naming remains English.
- Frontend labels/messages remain Turkish.
- The system starts as single-tenant in practice, but database design must allow future multi-tenant SaaS expansion.
- The tenant concept is named `organization`.
- Authentication uses email + password.
- Passwords are stored only as secure hashes.
- JWT access tokens are used for API authentication.
- Access token target lifetime: 30 minutes.
- Refresh token target lifetime: 30 days, to be added after initial login flow.
- Authorization follows role-based access control with future permission support.
- Initial roles:
  - super_admin
  - admin
  - manager
  - sales
  - viewer
- JWT payload should include:
  - user_id
  - organization_id
  - email
  - role