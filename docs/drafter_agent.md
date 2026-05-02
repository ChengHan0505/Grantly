# Gemini generating React slide components

Because Gemini models are strong at frontend/code generation, you can ask Gemini to output React/Tailwind slide components instead of raw PPTX.

Workflow:

```md
Content JSON
   ↓
Gemini generates React component for each slide
   ↓
Render inside your web app
   ↓
Screenshot/export to PDF
```

Example content:
1. Company Overview
2. Problem / Need
3. Proposed Solution
4. Social / Economic Impact
5. Market Opportunity
6. Implementation Plan
7. Budget Usage
8. Team Capability
9. Risk & Mitigation
10. Expected Outcomes
11. Grant Alignment
12. Closing / Funding Request

Example prompt:

You are a senior presentation designer.

Convert this slide JSON into a single React + Tailwind component.
Rules:
- 16:9 slide, 1600x900
- Government grant pitch deck style
- Professional SME funding aesthetic
- Use cards, visual hierarchy, icons, and diagrams
- Do not use external paid assets
- Return code only
My recommended approach for your hackathon

Use this architecture:

```md
Gemini content agent
   ↓
Gemini layout agent
   ↓
React slide renderer
   ↓
Browser preview/editor
   ↓
Export to PDF
```

Do not generate .pptx first.

Build it like Gamma/Tome-style web slides, not PowerPoint-style slides.

That gives you:

more generative layouts
better visual design
editable website experience
easier animation
easier multilingual support
no boring python-pptx templates

Best MVP choice:

Generate a web-based pitch deck first, export as PDF later.

## Current backend MVP

For the FastAPI MVP, the Drafter Agent now also supports direct PPTX output from a compact SME profile payload:

```md
SME profile JSON
   ↓
Deterministic slide planner
   ↓
Dependency-free PPTX writer
   ↓
Download .pptx
```

This path intentionally avoids sending the full profile, grant database, or a long JSON schema to the model. It uses the normalized SME profile fields directly, so runtime token usage is effectively zero for PPTX creation.

Endpoint:

```http
POST /grants/drafter/pitch-deck
```

For Gemini-assisted creative layouts:

```http
POST /grants/drafter/pitch-deck/creative
```

Set the API token in your console or `.env`; never paste it into the request body:

```powershell
$env:GOOGLE_API_KEY="your-token-here"
```

Request:

```json
{
  "sme_profile": {
    "company_name": "YAP Sdn Bhd",
    "sector": "ICT",
    "full_time_employees": 5,
    "age_in_months": 24,
    "requested_funding_rm": 250000,
    "total_project_cost_rm": 500000,
    "outsourced_cost_rm": 20000,
    "has_end_user_partner": true
  },
  "grant_context": {
    "grant_name": "MDEC MDCG",
    "provider_name": "MDEC"
  },
  "filename": "yap_mdec_pitch_deck.pptx"
}
```

Stored application profiles can also download:

```http
GET /grants/{grant_id}/application/{user_id}/pitch-deck.pptx
```

For the real app flow, generate and store the deck first:

```http
POST /grants/{grant_id}/application/{user_id}/pitch-deck/generate
```

Request:

```json
{
  "creative": true,
  "filename": "application_pitch_deck.pptx",
  "extra_context": {}
}
```

This calls Gemini with `settings.google_api_key`, renders the returned slide plan into a `.pptx`, stores the file as a generated `CompanyDocument` tied to `user_id`, and returns a `download_url`.
