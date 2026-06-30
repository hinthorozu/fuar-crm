# FAIR CRM

FAIR CRM is a web-based CRM product for managing fair exhibitors, customers, contacts, participations and future import/scraper workflows.

## Current Version

`v0.1.9` — master stabilization: version sync, full 13-table health check and import mapping alignment.

## Standard Project Structure

```text
fair-crm/
├── backend/                  # FastAPI backend
├── frontend/                 # React frontend target
├── docs/                     # ER diagrams, mockups, Postman/Swagger exports, samples
├── resources/                # Logos, icons, Excel templates, import files, branding
├── scripts/                  # Helper scripts
├── README.md                 # Project overview and quick start
├── MASTER_CONTEXT.md         # Project memory and permanent rules
├── CHANGELOG.md              # Version history
├── FAIR_CRM_PROJECT.xlsx     # Main project hub / single source of truth
├── docker-compose.yml
├── .gitignore
└── LICENSE
```

## Quick Start

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Create your local `.env`

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Then open `backend/.env` and set your MySQL password:

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fair_crm
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_ALLOW_EMPTY_PASSWORD=false
```

If your local MySQL user intentionally has no password, use:

```env
DB_ALLOW_EMPTY_PASSWORD=true
```

### 3. Create database and seed data

Make sure the database exists in MySQL:

```sql
CREATE DATABASE fair_crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then run:

```bash
python init_db.py
python seed.py --reset
```

### 4. Start API

```bash
uvicorn app.main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```


### 5. Run local health check

After `.env`, database creation and seed steps, run the automated project check from the project root:

```bash
python scripts/health_check.py
```

This command validates:

```text
.env file and required DB values
Database connection
Required tables
Seed row counts
FastAPI app import
Key API route registration
Project Excel hub presence
```

Expected final result:

```text
Result: SYSTEM READY
```

## Main Test Endpoints

```text
GET /dashboard/summary
GET /customers
GET /customers/1/profile
GET /fair-participations
```

## Environment Rule

Real credentials must stay in `backend/.env`. This file is ignored by Git.
Use `backend/.env.example` as the safe template.

## Documentation Rule

Project management information such as roadmap, database dictionary, API list, business rules, import mapping, tests, bugs, ideas and decisions lives in:

```text
FAIR_CRM_PROJECT.xlsx
```

Root Markdown files are intentionally limited to `README.md`, `MASTER_CONTEXT.md` and `CHANGELOG.md`.


## Development Check

Run before every commit:

```bash
python scripts/dev_check.py
```
