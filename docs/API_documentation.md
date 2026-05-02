# Grantly API Documentation

## Overview

Grantly is a FastAPI backend for the pipeline in `docs/execution.md` and `docs/pipeline.md`:

1. Hybrid onboarding and Extractor profile generation.
2. Scout grant discovery.
3. Evaluator ranked matching with evidence traces.
4. Coach or Drafter application flow based on an 80% readiness threshold.
5. Submission package download for manual portal submission.

Base URL: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

## Common Contracts

Readiness and suitability scores are percentages from `0` to `100`.

Requirement `source_type` values:

- `attached`: hard documents the SME must upload, such as SSM or audited financial statements.
- `generated`: soft documents the Drafter Agent can create, such as proposals, pitch decks, or company profiles.

Errors return:

```json
{ "detail": "Message describing the error." }
```

## Health

### `GET /`

Returns backend status and model metadata.

```json
{
  "status": "online",
  "model": "gemini-2.5-flash",
  "service": "Grantly"
}
```

## Users And Onboarding

### `POST /users`

Registers a user account. Clerk or another auth provider can pass its user id through `external_auth_id`.

Request:

```json
{
  "username": "yap_founder",
  "email": "founder@example.com",
  "external_auth_id": "clerk_user_id"
}
```

Response: `201 UserRead`

### `GET /users/{user_id}`

Returns user details.

### `PUT /users/{user_id}/company-profile`

Creates or updates a normalized company profile directly.

Request:

```json
{
  "company_name": "YAP Sdn Bhd",
  "industry": "ICT",
  "nationality": "Malaysia",
  "annual_revenue": 500000,
  "employee_count": 5,
  "target_grant_amount": 250000,
  "business_stage": "growth",
  "summary": "Local ICT SME applying for digitalisation funding.",
  "questionnaire_answers": {},
  "extracted_data": {},
  "documents": [
    {
      "document_type": "ssm",
      "file_name": "SSM Certificate.pdf",
      "file_url": null,
      "status": "uploaded",
      "metadata": {}
    }
  ]
}
```

Response: `CompanyProfileRead` with `readiness_score` as `0-100`.

### `POST /users/{user_id}/company-profile/extract`

Hybrid onboarding endpoint. Accepts questionnaire answers, document metadata, and/or Extractor Agent JSON shaped like the sandbox output.

Request:

```json
{
  "raw_text": "YAP Sdn Bhd is a local ICT company...",
  "questionnaire_answers": {
    "annual_revenue": 500000
  },
  "extractor_profile": {
    "company_name": "YAP Sdn Bhd",
    "ssm_number": "1234567-V",
    "age_in_months": 24,
    "full_time_employees": 5,
    "ownership_majority": "Local",
    "sector": "ICT",
    "total_project_cost_rm": 500000,
    "requested_funding_rm": 250000,
    "outsourced_cost_rm": 20000,
    "has_end_user_partner": true,
    "documents_provided": ["SSM Certificate", "Pitch Deck"]
  },
  "documents": []
}
```

Response:

```json
{
  "profile": { "id": 1, "user_id": 1, "company_name": "YAP Sdn Bhd", "readiness_score": 80.0 },
  "documents": [],
  "system_state": { "user_id": 1, "readiness_score": 80.0, "current_track": "grant_matching" },
  "next_endpoint": "/grants/match/1"
}
```

### `GET /users/{user_id}/company-profile`

Returns the generated profile.

### `GET /users/{user_id}/documents`

Returns uploaded and generated company documents.

### `GET /users/{user_id}/system-state`

Returns the user's current pipeline state.

## Grants And Evaluator

### `GET /grants`

Lists all grants in the database for the Grant tab.

### `POST /grants`

Creates a grant record, normally from Scout.

Request:

```json
{
  "title": "MDEC MDCG",
  "provider_name": "MDEC",
  "source_url": "https://example.com/grant",
  "description": "Digital grant for Malaysian SMEs.",
  "amount_min": 0,
  "amount_max": 1000000,
  "nationality": "Malaysia",
  "industry": "ICT",
  "application_deadline": "2026-12-31",
  "status": "open",
  "metadata_json": {},
  "requirements": [
    {
      "name": "Audited Financials",
      "description": "Latest audited financial statements.",
      "source_type": "attached",
      "document_type": "financial_statement",
      "is_required": true
    },
    {
      "name": "Pitch Deck",
      "source_type": "generated",
      "document_type": "pitch_deck",
      "is_required": true
    }
  ]
}
```

Response: `201 GrantRead`

### `POST /grants/drafter/pitch-deck`

Generates a `.pptx` pitch deck directly from a compact SME profile payload. This path is deterministic and does not call the LLM, keeping token usage minimal.

Request:

```json
{
  "sme_profile": {
    "company_name": "YAP Sdn Bhd",
    "sector": "ICT",
    "full_time_employees": 5,
    "age_in_months": 24,
    "requested_funding_rm": 250000,
    "total_project_cost_rm": 500000
  },
  "grant_context": {
    "grant_name": "MDEC MDCG",
    "provider_name": "MDEC"
  },
  "filename": "yap_mdec_pitch_deck.pptx"
}
```

Response: PowerPoint file download.

### `POST /grants/drafter/pitch-deck/creative`

Uses Gemini 2.5 Flash to create a compact creative layout plan, then renders it into `.pptx` locally. Set `GOOGLE_API_KEY` in `.env` or your console; do not send the token in the JSON body.

Request body is the same as `POST /grants/drafter/pitch-deck`.

Response: PowerPoint file download.

For user-tied application storage, prefer the application endpoint below.

### `GET /grants/match/{user_id}`

Runs the Evaluator-style ranking over the grant database.

Response:

```json
[
  {
    "grant": { "id": 1, "title": "MDEC MDCG" },
    "suitability_score": 85.0,
    "readiness_score": 75.0,
    "readiness_level": "75% Ready",
    "track": "coach",
    "status": "needs_documents",
    "reasons": ["Industry matches the grant focus."],
    "evidence_traces": [
      {
        "requirement": "Mandatory document: Audited Financials",
        "status": "UNMET",
        "source_document": "Company Documents",
        "reasoning": "Audited Financials still needs to be uploaded."
      }
    ]
  }
]
```

### `GET /grants/{grant_id}`

Returns full grant details.

## Application Flow

### `GET /grants/{grant_id}/application/{user_id}`

Returns the grant application page payload: checklist, readiness score, branch, hard docs, generated docs, and Coach steps when readiness is below `80`.

Response:

```json
{
  "grant": { "id": 1, "title": "MDEC MDCG" },
  "checklist": [
    {
      "requirement_id": 10,
      "name": "Pitch Deck",
      "source_type": "generated",
      "document_type": "pitch_deck",
      "is_required": true,
      "fulfilled": false,
      "fulfillment_source": null,
      "category": "generated",
      "completion_status": "generatable",
      "can_generate": true,
      "can_upload": false,
      "download_url": null,
      "action_label": "Generate document"
    }
  ],
  "readiness_score": 75.0,
  "readiness_level": "75% Ready",
  "track": "coach",
  "missing_required_documents": ["Audited Financials"],
  "attached_documents": [],
  "generated_documents": [],
  "coach": {
    "encouraging_message": "You are close. These missing items are a practical checklist, not a rejection.",
    "next_steps": []
  },
  "download_package_url": "/grants/1/application/1/package"
}
```

### `POST /grants/{grant_id}/application/{user_id}/documents/generate`

Calls the Drafter path for a generated requirement and stores the output as a generated company document.

Request:

```json
{
  "requirement_id": 10,
  "document_type": "pitch_deck",
  "document_name": "Pitch Deck",
  "regenerate": false,
  "extra_context": {}
}
```

Response:

```json
{
  "document": { "id": 5, "document_type": "pitch_deck", "status": "generated" },
  "requirement_id": 10,
  "document_type": "pitch_deck",
  "content_markdown": "# YAP Sdn Bhd Pitch Deck...",
  "message": "Generated document is ready for the submission package."
}
```

### `POST /grants/{grant_id}/application/{user_id}/draft`

Runs the ready-track Drafter bundle. This endpoint requires the application snapshot to be on the `drafter` track; otherwise it returns `409` with the missing hard documents.

Request:

```json
{
  "uploaded_pitch_deck_text": null,
  "extra_context": {}
}
```

Response:

```json
{
  "business_proposal_markdown": "YAP Sdn Bhd is...",
  "presentation_script_markdown": "Good day...",
  "generated_deck": [
    {
      "slide_number": 1,
      "title": "Problem and Solution",
      "bullet_points": ["..."]
    }
  ],
  "deck_critique": null,
  "generated_documents": []
}
```

### `POST /grants/{grant_id}/application/{user_id}/pitch-deck/generate`

Calls Gemini 2.5 Flash with `GOOGLE_API_KEY` from backend settings, renders the creative slide plan into `.pptx`, and stores the file in the user's document database as a generated `pitch_deck` document.

Request:

```json
{
  "creative": true,
  "filename": "yap_mdec_pitch_deck.pptx",
  "extra_context": {}
}
```

Response:

```json
{
  "document": {
    "id": 8,
    "document_type": "pitch_deck",
    "file_name": "yap_mdec_pitch_deck.pptx",
    "status": "generated",
    "content_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "generation_mode": "gemini_creative",
    "created_at": "2026-04-25T12:00:00"
  },
  "download_url": "/grants/1/application/1/documents/8/download",
  "message": "Pitch deck generated by Drafter Agent and stored in the user document database.",
  "layout_plan": {}
}
```

### `GET /grants/{grant_id}/application/{user_id}/package`

Downloads a ZIP package containing:

- `application_manifest.json`
- `company_profile.md`
- `generated/pitch_deck.pptx`
- generated markdown documents under `generated/`
- `uploaded_documents_manifest.json` for hard-doc file references

### `GET /grants/{grant_id}/application/{user_id}/documents/{document_id}/download`

Downloads a stored generated document directly. PPTX documents are decoded from database metadata and streamed as PowerPoint files. Generated markdown documents are streamed as text. For uploaded hard documents, returns the document-vault file reference because the API stores metadata rather than raw binary uploads.

### `GET /grants/{grant_id}/application/{user_id}/pitch-deck.pptx`

Downloads the latest stored pitch deck for this user and grant. Call `POST /grants/{grant_id}/application/{user_id}/pitch-deck/generate` first.

## Scout

### `POST /grants/scout/start`

Starts the Scout Agent in the background.

Request:

```json
{
  "run_mode": "curated",
  "source_file": null,
  "max_links_per_page": 0
}
```

Response: `202 ScoutStatusRead`

### `POST /grants/scout/stop`

Requests Scout to stop at the next safe checkpoint.

### `GET /grants/scout/status`

Returns in-process Scout state.

### `POST /grants/scout/run`

Runs the curated Scout synchronously. Kept for demos and backward compatibility.

### `GET /grants/scout/last-report`

Returns the persisted last Scout report.

### `GET /grants/scout/source-health`

Checks curated source URLs and returns health status.
