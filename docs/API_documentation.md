# Grantly API Documentation

## Overview

**Grantly** is a FastAPI-based backend application designed to help Malaysian SMEs discover and apply for grants matching their business profile. The API provides endpoints for user management, company profiling, grant discovery, and application tracking.

**Base URL:** `http://localhost:8000`  
**Version:** 1.0.0  
**Model:** GLM-5.1-Agentic

---

## Table of Contents

1. [Authentication](#authentication)
2. [Error Handling](#error-handling)
3. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [User Management](#user-management)
   - [Grants](#grants)
4. [Data Models](#data-models)
5. [Testing](#testing)

---

## Authentication

Currently, no authentication is required. All endpoints are publicly accessible. CORS is enabled for all origins.

---

## Error Handling

All errors return a JSON response with the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- **200 OK** - Request succeeded
- **201 Created** - Resource created successfully
- **400 Bad Request** - Invalid request parameters
- **404 Not Found** - Resource not found
- **409 Conflict** - Resource conflict (e.g., duplicate user)
- **500 Internal Server Error** - Server error

---

## Endpoints

### Health Check

#### `GET /`

Check if the server is running and get system information.

**Response:** 200 OK

```json
{
  "status": "online",
  "model": "GLM-5.1-Agentic",
  "service": "Grantly"
}
```

**Example cURL:**
```bash
curl http://localhost:8000/
```

---

### User Management

#### `POST /users`

Register a new user account.

**Request Body:**

```json
{
  "username": "string (3-80 chars)",
  "email": "string",
  "external_auth_id": "string or null (optional)"
}
```

**Response:** 201 Created

```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "external_auth_id": "auth_id_123",
  "created_at": "2026-04-21T12:34:56"
}
```

**Error Cases:**
- `409 Conflict` - Username or email already exists

**Example cURL:**
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "external_auth_id": "oauth_123"
  }'
```

---

#### `GET /users/{user_id}`

Retrieve user details by ID.

**Path Parameters:**
- `user_id` (int, required) - The user ID

**Response:** 200 OK

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "external_auth_id": "oauth_123",
  "created_at": "2026-04-21T12:34:56"
}
```

**Error Cases:**
- `404 Not Found` - User does not exist

**Example cURL:**
```bash
curl http://localhost:8000/users/1
```

---

#### `PUT /users/{user_id}/company-profile`

Create or update a company profile for a user. This endpoint also manages associated documents.

**Path Parameters:**
- `user_id` (int, required) - The user ID

**Request Body:**

```json
{
  "company_name": "string (required)",
  "industry": "string or null",
  "nationality": "string or null",
  "annual_revenue": "number or null",
  "employee_count": "integer or null",
  "target_grant_amount": "number or null",
  "business_stage": "string or null (e.g., 'startup', 'growth', 'established')",
  "summary": "string or null",
  "questionnaire_answers": "object (optional)",
  "extracted_data": "object (optional)",
  "documents": [
    {
      "document_type": "string (e.g., 'financial_statement', 'business_plan')",
      "file_name": "string",
      "file_url": "string or null",
      "status": "string (default: 'uploaded')",
      "metadata": "object (optional)"
    }
  ]
}
```

**Response:** 200 OK

```json
{
  "id": 1,
  "user_id": 1,
  "company_name": "Tech Innovations Ltd",
  "industry": "Technology",
  "nationality": "Malaysia",
  "annual_revenue": 500000,
  "employee_count": 15,
  "target_grant_amount": 100000,
  "business_stage": "growth",
  "summary": "An innovative tech startup focused on AI solutions",
  "questionnaire_answers": {},
  "extracted_data": {},
  "readiness_score": 0.75,
  "created_at": "2026-04-21T12:34:56",
  "updated_at": "2026-04-21T12:34:56"
}
```

**Error Cases:**
- `404 Not Found` - User does not exist

**Example cURL:**
```bash
curl -X PUT http://localhost:8000/users/1/company-profile \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Innovations Ltd",
    "industry": "Technology",
    "nationality": "Malaysia",
    "annual_revenue": 500000,
    "employee_count": 15,
    "target_grant_amount": 100000,
    "business_stage": "growth",
    "summary": "An innovative tech startup focused on AI solutions",
    "documents": [
      {
        "document_type": "financial_statement",
        "file_name": "2025_financial_report.pdf",
        "file_url": "https://example.com/files/report.pdf"
      }
    ]
  }'
```

---

#### `GET /users/{user_id}/company-profile`

Retrieve the company profile for a user.

**Path Parameters:**
- `user_id` (int, required) - The user ID

**Response:** 200 OK

```json
{
  "id": 1,
  "user_id": 1,
  "company_name": "Tech Innovations Ltd",
  "industry": "Technology",
  "nationality": "Malaysia",
  "annual_revenue": 500000,
  "employee_count": 15,
  "target_grant_amount": 100000,
  "business_stage": "growth",
  "summary": "An innovative tech startup focused on AI solutions",
  "questionnaire_answers": {},
  "extracted_data": {},
  "readiness_score": 0.75,
  "created_at": "2026-04-21T12:34:56",
  "updated_at": "2026-04-21T12:34:56"
}
```

**Error Cases:**
- `404 Not Found` - Company profile not found

**Example cURL:**
```bash
curl http://localhost:8000/users/1/company-profile
```

---

#### `GET /users/{user_id}/documents`

List all documents associated with a user's company profile.

**Path Parameters:**
- `user_id` (int, required) - The user ID

**Response:** 200 OK

```json
[
  {
    "id": 1,
    "document_type": "financial_statement",
    "file_name": "2025_financial_report.pdf",
    "file_url": "https://example.com/files/report.pdf",
    "status": "uploaded",
    "metadata_json": {},
    "created_at": "2026-04-21T12:34:56"
  },
  {
    "id": 2,
    "document_type": "business_plan",
    "file_name": "business_plan.pdf",
    "file_url": "https://example.com/files/plan.pdf",
    "status": "uploaded",
    "metadata_json": {},
    "created_at": "2026-04-21T12:34:56"
  }
]
```

**Error Cases:**
- `404 Not Found` - User does not exist

**Example cURL:**
```bash
curl http://localhost:8000/users/1/documents
```

---

#### `GET /users/{user_id}/system-state`

Retrieve the system state for a user (readiness score, current track, etc.).

**Path Parameters:**
- `user_id` (int, required) - The user ID

**Response:** 200 OK

```json
{
  "user_id": 1,
  "readiness_score": 0.75,
  "current_track": "grant_discovery",
  "evidence_trace": {},
  "last_step": "profile_completion",
  "updated_at": "2026-04-21T12:34:56"
}
```

**Error Cases:**
- `404 Not Found` - System state not found for user

**Example cURL:**
```bash
curl http://localhost:8000/users/1/system-state
```

---

### Grants

#### `POST /grants`

Create a new grant record in the system.

**Request Body:**

```json
{
  "title": "string (required)",
  "provider_name": "string (required)",
  "source_url": "string or null",
  "description": "string or null",
  "amount_min": "number or null",
  "amount_max": "number or null",
  "nationality": "string or null",
  "industry": "string or null",
  "eligibility_notes": "string or null",
  "application_deadline": "string or null (ISO format)",
  "status": "string (default: 'open')",
  "metadata_json": "object (optional)",
  "requirements": [
    {
      "name": "string (required)",
      "description": "string or null",
      "source_type": "enum ('manual' | 'extracted' | 'inferred')",
      "document_type": "string or null",
      "is_required": "boolean (default: true)"
    }
  ]
}
```

**Response:** 201 Created

```json
{
  "id": 1,
  "title": "SME Tech Innovation Grant",
  "provider_name": "Ministry of Science & Technology",
  "source_url": "https://example.com/grant",
  "description": "Funding for tech startups developing innovative solutions",
  "amount_min": 50000,
  "amount_max": 500000,
  "nationality": "Malaysia",
  "industry": "Technology",
  "eligibility_notes": "Must be registered SME",
  "application_deadline": "2026-12-31",
  "status": "open",
  "metadata_json": {},
  "created_at": "2026-04-21T12:34:56",
  "updated_at": "2026-04-21T12:34:56",
  "requirements": [
    {
      "id": 1,
      "name": "Financial Statement",
      "description": "Latest 2-year financial statement",
      "source_type": "manual",
      "document_type": "financial_statement",
      "is_required": true
    }
  ]
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/grants \
  -H "Content-Type: application/json" \
  -d '{
    "title": "SME Tech Innovation Grant",
    "provider_name": "Ministry of Science & Technology",
    "source_url": "https://example.com/grant",
    "description": "Funding for tech startups",
    "amount_min": 50000,
    "amount_max": 500000,
    "nationality": "Malaysia",
    "industry": "Technology",
    "application_deadline": "2026-12-31",
    "requirements": [
      {
        "name": "Financial Statement",
        "source_type": "manual",
        "is_required": true
      }
    ]
  }'
```

---

#### `GET /grants/{grant_id}`

Retrieve detailed information about a specific grant.

**Path Parameters:**
- `grant_id` (int, required) - The grant ID

**Response:** 200 OK

```json
{
  "id": 1,
  "title": "SME Tech Innovation Grant",
  "provider_name": "Ministry of Science & Technology",
  "source_url": "https://example.com/grant",
  "description": "Funding for tech startups developing innovative solutions",
  "amount_min": 50000,
  "amount_max": 500000,
  "nationality": "Malaysia",
  "industry": "Technology",
  "eligibility_notes": "Must be registered SME",
  "application_deadline": "2026-12-31",
  "status": "open",
  "metadata_json": {},
  "created_at": "2026-04-21T12:34:56",
  "updated_at": "2026-04-21T12:34:56",
  "requirements": [
    {
      "id": 1,
      "name": "Financial Statement",
      "description": "Latest 2-year financial statement",
      "source_type": "manual",
      "document_type": "financial_statement",
      "is_required": true
    }
  ]
}
```

**Error Cases:**
- `404 Not Found` - Grant does not exist

**Example cURL:**
```bash
curl http://localhost:8000/grants/1
```

---

#### `GET /grants/match/{user_id}`

Get a ranked list of grants matching a user's company profile.

**Path Parameters:**
- `user_id` (int, required) - The user ID

**Response:** 200 OK

```json
[
  {
    "grant": {
      "id": 1,
      "title": "SME Tech Innovation Grant",
      "provider_name": "Ministry of Science & Technology",
      "source_url": "https://example.com/grant",
      "description": "Funding for tech startups developing innovative solutions",
      "amount_min": 50000,
      "amount_max": 500000,
      "nationality": "Malaysia",
      "industry": "Technology",
      "eligibility_notes": "Must be registered SME",
      "application_deadline": "2026-12-31",
      "status": "open",
      "metadata_json": {},
      "created_at": "2026-04-21T12:34:56",
      "updated_at": "2026-04-21T12:34:56",
      "requirements": []
    },
    "suitability_score": 0.92,
    "status": "matched",
    "reasons": [
      "Industry matches: Technology",
      "Matching nationality requirement: Malaysia",
      "Grant amount aligns with target: 100,000 requested"
    ]
  }
]
```

**Error Cases:**
- `404 Not Found` - User does not exist

**Example cURL:**
```bash
curl http://localhost:8000/grants/match/1
```

---

#### `GET /grants/{grant_id}/application/{user_id}`

Get the grant application snapshot including a checklist of requirements and user's fulfillment status.

**Path Parameters:**
- `grant_id` (int, required) - The grant ID
- `user_id` (int, required) - The user ID

**Response:** 200 OK

```json
{
  "grant": {
    "id": 1,
    "title": "SME Tech Innovation Grant",
    "provider_name": "Ministry of Science & Technology",
    "source_url": "https://example.com/grant",
    "description": "Funding for tech startups",
    "amount_min": 50000,
    "amount_max": 500000,
    "nationality": "Malaysia",
    "industry": "Technology",
    "eligibility_notes": "Must be registered SME",
    "application_deadline": "2026-12-31",
    "status": "open",
    "metadata_json": {},
    "created_at": "2026-04-21T12:34:56",
    "updated_at": "2026-04-21T12:34:56",
    "requirements": []
  },
  "checklist": [
    {
      "requirement_id": 1,
      "name": "Financial Statement",
      "description": "Latest 2-year financial statement",
      "source_type": "manual",
      "document_type": "financial_statement",
      "is_required": true,
      "fulfilled": true,
      "fulfillment_source": "uploaded_document_1",
      "action_label": "✓ Provided"
    },
    {
      "requirement_id": 2,
      "name": "Business Plan",
      "description": "Current business plan",
      "source_type": "manual",
      "document_type": "business_plan",
      "is_required": true,
      "fulfilled": false,
      "fulfillment_source": null,
      "action_label": "Upload required"
    }
  ]
}
```

**Error Cases:**
- `404 Not Found` - Grant not found

**Example cURL:**
```bash
curl http://localhost:8000/grants/1/application/1
```

---

## Data Models

### User Model

```typescript
{
  id: integer,
  username: string (3-80 characters),
  email: string,
  external_auth_id: string | null,
  created_at: datetime
}
```

### Company Profile

```typescript
{
  id: integer,
  user_id: integer,
  company_name: string,
  industry: string | null,
  nationality: string | null,
  annual_revenue: number | null,
  employee_count: integer | null,
  target_grant_amount: number | null,
  business_stage: string | null,
  summary: string | null,
  questionnaire_answers: object,
  extracted_data: object,
  readiness_score: float,
  created_at: datetime,
  updated_at: datetime
}
```

### Document

```typescript
{
  id: integer,
  document_type: string,
  file_name: string,
  file_url: string | null,
  status: string,
  metadata_json: object,
  created_at: datetime
}
```

### Grant

```typescript
{
  id: integer,
  title: string,
  provider_name: string,
  source_url: string | null,
  description: string | null,
  amount_min: number | null,
  amount_max: number | null,
  nationality: string | null,
  industry: string | null,
  eligibility_notes: string | null,
  application_deadline: string | null (ISO format),
  status: string,
  metadata_json: object,
  created_at: datetime,
  updated_at: datetime,
  requirements: Requirement[]
}
```

### Requirement

```typescript
{
  id: integer,
  name: string,
  description: string | null,
  source_type: 'manual' | 'extracted' | 'inferred',
  document_type: string | null,
  is_required: boolean
}
```

### Ranked Grant

```typescript
{
  grant: Grant,
  suitability_score: float (0-1),
  status: string,
  reasons: string[]
}
```

### Grant Application

```typescript
{
  grant: Grant,
  checklist: ChecklistItem[]
}
```

### Checklist Item

```typescript
{
  requirement_id: integer,
  name: string,
  description: string | null,
  source_type: 'manual' | 'extracted' | 'inferred',
  document_type: string | null,
  is_required: boolean,
  fulfilled: boolean,
  fulfillment_source: string | null,
  action_label: string
}
```

### System State

```typescript
{
  user_id: integer,
  readiness_score: float,
  current_track: string,
  evidence_trace: object,
  last_step: string | null,
  updated_at: datetime
}
```

---

## Testing

### Interactive API Documentation

Once the server is running, visit these URLs for interactive testing:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Quick Test Workflow

1. **Create a User**
   ```bash
   curl -X POST http://localhost:8000/users \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","email":"test@example.com"}'
   ```
   Note the returned `id` (e.g., 1)

2. **Create a Company Profile**
   ```bash
   curl -X PUT http://localhost:8000/users/1/company-profile \
     -H "Content-Type: application/json" \
     -d '{
       "company_name":"Test Company",
       "industry":"Technology",
       "nationality":"Malaysia",
       "employee_count":10
     }'
   ```

3. **Create a Grant**
   ```bash
   curl -X POST http://localhost:8000/grants \
     -H "Content-Type: application/json" \
     -d '{
       "title":"Test Grant",
       "provider_name":"Test Provider",
       "industry":"Technology",
       "nationality":"Malaysia"
     }'
   ```
   Note the returned `id` (e.g., 1)

4. **Get Matching Grants**
   ```bash
   curl http://localhost:8000/grants/match/1
   ```

5. **View Grant Application**
   ```bash
   curl http://localhost:8000/grants/1/application/1
   ```

---

## Additional Resources

- **GitHub Repository:** [Grantly](https://github.com/grantly)
- **Pitch Deck:** See `docs/pitch_deck.md`
- **Project Explanation:** See `docs/project_explanation`
- **Execution Plan:** See `docs/execution_plan.md`

---

**Last Updated:** April 21, 2026  
**API Status:** ✓ Active
