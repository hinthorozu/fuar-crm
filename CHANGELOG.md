## v0.2.2 - Authentication Foundation

### Added
- Added JWT configuration via `backend/.env` (`SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`).
- Added authentication service layer at `app/services/auth_service.py`.
- Added auth schemas, dependencies, and router with `POST /auth/login` and `GET /auth/me`.
- Added admin-oriented dependency helper for future protected admin endpoints.

### Changed
- Hardened `app/security.py` to load JWT settings from config and reject unsafe secrets.
- JWT payload now includes `user_id`, `organization_id`, `email`, and `role`.
- Seed admin handling is idempotent when the admin user already exists.
- Health check and quality check now validate auth route registration.

### Security
- Plain passwords are never stored.
- Invalid credentials return `401`; inactive users return `403`.

## v0.2.1 - Quality Check Automation

### Added
- Added `scripts/quality_check.py` as the comprehensive pre-commit quality gate.
- Validates Python compile, backend imports, FastAPI app, SQLAlchemy models, router registration, requirements consistency, environment variables, project structure, required project files, TODO/FIXME markers, circular imports, health check, and dev check.
- Reports quality score, warnings, git working tree status, and commit readiness.

### Changed
- Git working tree status is informational only (`CLEAN` or `MODIFIED`) and never fails the quality gate.
- TODO/FIXME markers produce warnings and reduce the quality score instead of hard failure.

## v0.2.0 - Auth Foundation

### Added
- Added authentication design decisions for future SaaS support.
- Added JWT/security helper foundation.
- Added password hashing and verification helpers.

### Technical Decisions
- Tenant concept will be named `organization`.
- Login will use email + password.
- Authorization will start with RBAC and remain permission-ready.

## v0.1.10
- Added development check workflow.
- Health check route validation stabilized.
- Project marked as SYSTEM READY.

# CHANGELOG

## v0.1.9 - Route registration health-check fix

- `app.main` now uses explicit `create_app()` construction and router registration.
- `scripts/health_check.py` now reports the exact imported `app.main` file to detect stale imports.
- Key route validation remains normalized for trailing slashes.


## v0.1.9 - Master Stabilization

### Changed
- Synchronized backend API version with project documentation.
- Cleaned duplicate router imports in `backend/app/main.py`.
- Extended local health check table and row checks to all 13 backend tables.
- Aligned Excel import mapping target columns with current backend models.

### Fixed
- Root API and health-check API now expose the synchronized project version.

## v0.1.7 - Health Check Route Normalization

### Fixed
- Health check route validation now treats `/customers` and `/customers/` as equivalent.
- Added route listing detail when key API route validation fails.


## v0.1.6 - Health Check Automation

### Added
- Added `scripts/health_check.py` for local automated project checks.
- Checks `.env`, database connectivity, required tables, seed row counts, FastAPI app import and key API routes.

### Changed
- README updated with health check usage.
- MASTER_CONTEXT updated with local verification standard.


## v0.1.5 - 2026-06-30

### Added
- Added `backend/app/config.py` for centralized environment-based settings.
- Added clear `.env` setup flow using `backend/.env.example`.
- Added safe support for either individual `DB_*` variables or full `DATABASE_URL` override.

### Changed
- Updated `backend/app/database.py` to read database configuration from `app.config.settings`.
- Updated `README.md` with `.env` creation and MySQL setup steps.
- Updated `FAIR_CRM_PROJECT.xlsx` with environment configuration decision and release history.

### Fixed
- Improved the previous confusing MySQL `Access denied ... using password: NO` situation by requiring `DB_PASSWORD` unless `DB_ALLOW_EMPTY_PASSWORD=true` is explicitly set.

## v0.1.4 - 2026-06-30

### Added
- Simplified standard project structure.
- Added `FAIR_CRM_PROJECT.xlsx` as central project hub.
- Added `docs/`, `resources/` and `scripts/` standard folders.

### Changed
- Reduced root Markdown documents to `README.md`, `MASTER_CONTEXT.md` and `CHANGELOG.md`.
- Moved project management information into Excel project hub.

## v0.1.3 - 2026-06-30

### Added
- Excel project hub introduced.

## v0.1.2 - 2026-06-30

### Added
- Product development standard documents.

## v0.1.1 - 2026-06-30

### Fixed
- MySQL/MariaDB JSON compatibility fix.

## v0.1.0 - 2026-06-30

### Added
- Usable CRM endpoints.
- Dashboard summary endpoint.
- Customer profile endpoint.
- Development seed data.
