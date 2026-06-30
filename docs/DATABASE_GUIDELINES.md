# FAIR CRM Database Guidelines

## Purpose

This document defines database standards for FAIR CRM.

Every schema change must follow these rules.

---

# General Principles

- English only.
- snake_case naming.
- Plural table names.
- Primary keys use integer auto increment.
- Foreign keys must be indexed.
- Never remove production columns without approval.

---

# Naming

Tables

customers

contacts

customer_phones

customer_emails

fairs

fair_participations

notes

users

organizations

roles

permissions

role_permissions

---

Columns

created_at

updated_at

deleted_at

created_by

updated_by

organization_id

customer_id

fair_id

---

# Relationships

Always define SQLAlchemy relationships.

Always define back_populates.

Never leave orphan records.

---

# Foreign Keys

Always use FK constraints.

Always create indexes.

---

# Audit

Future standard

created_at

updated_at

created_by

updated_by

deleted_at (Soft Delete)

---

# Soft Delete

Future feature.

Never permanently delete customer data unless explicitly requested.

---

# Import Engine

Import tables never write directly into CRM tables.

Workflow

Excel

↓

Import Batch

↓

Import Rows

↓

Duplicate Detection

↓

Merge

↓

Customer

---

# Duplicate Detection

Always normalize:

Company Name

Phone

Email

Website

Tax Number (future)

Similarity checks

Turkish character normalization

Legal suffix normalization

---

# Merge Rules

Never overwrite existing data automatically.

Always let user choose.

Prefer merge.

---

# Scraper

Scraper never inserts directly.

Always:

Scraper

↓

Import Engine

↓

CRM

---

# Indexes

Required

organization_id

customer_id

fair_id

email

phone

normalized_company_name

---

# Transactions

Use transactions for:

Import

Merge

Bulk update

Delete

---

# Migrations

Never modify production schema directly.

Schema evolution must be backward compatible.

---

# AI Rules

Never rename tables.

Never rename columns.

Never remove relationships.

Never redesign schema.

Always extend existing database.

Keep compatibility.