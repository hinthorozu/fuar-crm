
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
