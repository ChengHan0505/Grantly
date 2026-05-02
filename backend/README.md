# Grantly Backend

## Grant Scout Agent (Stage 1)

The scout is intentionally source-constrained and does not crawl the entire internet.

- Curated sources are loaded from `data/scout_runs/cradle_funds.json`, `data/scout_runs/mdec.json`, `data/scout_runs/mtdc_commercial_funds.json`, and `data/scout_runs/mtdc_development_funds.json`.
- Manual scout run only scrapes URLs listed in those curated files.
- Claude Sonnet is used first for structured extraction, with OpenRouter Gemini, direct Gemini, and Z.ai GLM as fallback providers when configured.
- Extracted records are saved locally in `data/scout_runs/run_<timestamp>.json` before any external deployment.
- Latest run report is persisted to `data/scout_runs/last_report.json`.

### Environment variables

Copy values into your local `.env`:

- `CLAUDE_SONNET_API_KEY` (primary provider)
- `CLAUDE_SONNET_MODEL` (default `claude-sonnet-4-5-20250929`)
- `OPENROUTER_GEMINI_API_KEY` or `OPENROUTER_API_KEY` (OpenRouter Gemini fallback)
- `OPENROUTER_GEMINI_MODEL` (default `google/gemini-2.5-flash`)
- `GOOGLE_API_KEY` (direct Gemini fallback)
- `GEMINI_MODEL` (default `gemini-2.5-flash`)
- `GEMINI_BASE_URL` (default `https://generativelanguage.googleapis.com/v1beta`)
- `ZAI_API_KEY` (optional fallback provider)
- `ZAI_MODEL` / `GLM_MODEL` (default `ilmu-glm-5.1`)
- `ZAI_BASE_URL` (default `https://api.ilmu.ai/v1`)
- `SCOUT_ENABLED` (`true`/`false`)
- `SCOUT_MAX_PAGES_PER_SOURCE`
- `SCOUT_MAX_LINKS_PER_PAGE`
- `SCOUT_MAX_CHARS_PER_PAGE`

### API endpoints

- `POST /grants/scout/run` to trigger a scout run manually.
- `GET /grants/scout/last-report` to fetch the latest run summary.

### Agent package

Backend agents now live in `backend/ai_sandbox/`. To test the Claude/Gemini provider chain from the project root:

```powershell
.\.venv\Scripts\python.exe -m backend.ai_sandbox.test_gemini_key
```
