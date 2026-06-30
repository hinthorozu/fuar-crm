
# FAIR CRM Coding Standards

## General Principles

- Keep code readable.
- Keep functions small.
- Prefer explicit code.
- Never duplicate logic.
- Never break existing architecture.

---

## Naming

Backend

English only

Examples

Customer

CustomerPhone

ImportBatch

ScraperRun

Frontend

Turkish only

Examples

Müşteriler

Fuarlar

İçe Aktar

---

## Folder Structure

Never create random folders.

Use existing project structure.

---

## Models

One responsibility per model.

Never duplicate tables.

Always define relationships.

Use SQLAlchemy typing.

---

## Schemas

Separate:

Request

Response

Internal

Never expose internal fields.

---

## Routers

One router per module.

Keep routers thin.

Business logic belongs outside routers when complexity grows.

---

## Database

English only.

snake_case

Plural table names.

Foreign keys always indexed.

Never delete production columns.

---

## Error Handling

Always return proper HTTP status.

Never expose internal exceptions.

---

## Validation

Validate all external input.

Never trust client data.

---

## Logging

Never print().

Use logging.

---

## Security

Never hardcode secrets.

Always use .env.

JWT only.

Passwords hashed.

---

## Imports

Avoid circular imports.

Prefer absolute imports.

---

## Documentation

Every sprint updates:

CHANGELOG.md

Architecture changes update:

MASTER_CONTEXT.md

Project progress updates:

FAIR_CRM_PROJECT.xlsx

---

## AI Rules

AI must analyze before coding.

AI must never redesign architecture.

AI must always run:

quality_check.py

health_check.py

before asking for commit.