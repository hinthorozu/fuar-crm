# FAIR CRM API Guidelines

## Purpose

This document defines the API standards used throughout FAIR CRM.

All backend endpoints must follow these rules.

---

# General Principles

- RESTful APIs only.
- English endpoint names.
- Consistent response format.
- Proper HTTP status codes.
- Backward compatibility is preferred.

---

# URL Naming

Good

/customers

/customers/{customer_id}

/fair-participations

/import-batches

Bad

/getCustomers

/customerList

/importBatch

---

# HTTP Methods

GET

Read

POST

Create

PUT

Replace

PATCH

Partial Update

DELETE

Delete

---

# Status Codes

200 OK

201 Created

204 No Content

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

500 Internal Server Error

---

# Response Format

Success

{
    "success": true,
    "data": {}
}

Error

{
    "success": false,
    "message": "",
    "errors": []
}

---

# Pagination

Future Standard

page

page_size

total

items

---

# Filtering

Use query parameters.

Example

/customers?city=istanbul

/customers?country=TR

---

# Sorting

Example

/customers?sort=name

/customers?sort=-created_at

---

# Searching

Example

/customers?q=bosch

---

# Authentication

JWT Bearer Token

Authorization

Bearer <token>

---

# Versioning

Current

No URL versioning.

Future

API v2 if breaking changes occur.

---

# Validation

Validate every request.

Never trust client input.

---

# Error Messages

Readable.

Consistent.

English.

---

# File Upload

Multipart/Form-Data

Future

Excel Import

Attachments

---

# Documentation

Swagger

OpenAPI

must always stay synchronized.

---

# AI Rules

Never rename existing endpoints.

Never change response format.

Prefer additive changes.

Never break frontend compatibility.