# FAIR CRM Architecture

Version: v0.2.1
Status: Active

---

# Purpose

FAIR CRM is a commercial SaaS CRM platform designed for exhibition and fair management.

This document describes the current architecture and the long-term architectural direction.

This is the primary reference for developers and AI assistants.

---

# Core Principles

- Improve the current architecture.
- Never redesign the project without approval.
- Keep the backend stable.
- Prefer incremental development.
- Documentation is part of the product.

---

# Technology Stack

Backend

- FastAPI
- SQLAlchemy
- MySQL
- Pydantic
- JWT Authentication

Frontend

- React (planned)

Database

- MySQL

Version Control

- Git
- GitHub

---

# High Level Architecture

Frontend

↓

REST API

↓

FastAPI

↓

Business Logic

↓

SQLAlchemy ORM

↓

MySQL

---

# Project Structure

backend/

Contains:

- API
- Models
- Routers
- Security
- Configuration
- Database

---

scripts/

Contains:

- dev_check.py
- health_check.py
- quality_check.py

---

docs/

Contains project documentation.

---

resources/

Static resources.

---

# Backend Layers

Configuration

↓

Security

↓

Database

↓

Models

↓

Schemas

↓

Routers

↓

Client

---

# Database Architecture

Main Entities

- Organizations
- Users
- Roles
- Permissions

CRM

- Customers
- Contacts
- Phones
- Emails
- Notes

Fair

- Fairs
- Fair Participations

Import

- Import Batches
- Import Rows

Scraper

- Scraper Sources
- Scraper Runs

Audit

- Audit Logs

---

# Authentication

JWT

Access Token

↓

Current User

↓

Permission Check

↓

Router

Future

- Refresh Token
- Multi Tenant

---

# Import Engine

Workflow

Excel

↓

Preview

↓

Validation

↓

Normalization

↓

Duplicate Detection

↓

Merge

↓

Import

↓

Audit Log

---

# Scraper

Website

↓

Parser

↓

Excel Export

↓

Import Engine

↓

CRM

Scrapers never write directly into CRM tables.

---

# Development Workflow

Analyze

↓

Plan

↓

Implement

↓

Quality Check

↓

Health Check

↓

Review

↓

Commit

↓

Push

---

# Validation Gates

Every sprint must pass

- quality_check.py
- dev_check.py
- health_check.py

before merge.

---

# Documentation

Every sprint updates

- CHANGELOG.md

When architecture changes

- MASTER_CONTEXT.md

Project progress

- FAIR_CRM_PROJECT.xlsx

---

# Versioning

Current

v0.2.x

Roadmap

v0.3.x

Import Engine

↓

v0.4.x

Scraper

↓

v0.5.x

Dashboard

↓

v1.0

Production SaaS

---

# Long Term Goals

- Multi Tenant SaaS
- Smart Import Engine
- Duplicate Detection
- Merge Wizard
- Scraper Framework
- Dashboard
- Reporting
- WhatsApp Integration
- AI Assistant
- Public API

---

End of Document