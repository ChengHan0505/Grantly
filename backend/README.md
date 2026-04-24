# Grantly Backend

## Grant Scout Agent (Stage 1)

The scout is intentionally source-constrained and does not crawl the entire internet.

- Curated sources are loaded from `data/scout_runs/cradle_funds.json`, `data/scout_runs/mdec.json`, `data/scout_runs/mtdc_commercial_funds.json`, and `data/scout_runs/mtdc_development_funds.json`.
- Manual scout run only scrapes URLs listed in those curated files.
- z.ai is used for minimal structured extraction from crawled pages.
- Extracted records are saved locally in `data/scout_runs/run_<timestamp>.json` before any external deployment.
- Latest run report is persisted to `data/scout_runs/last_report.json`.

### Environment variables

Copy values into your local `.env`:

- `ZAI_API_KEY`
- `ZAI_MODEL` (default `glm-4.5-flash`)
- `SCOUT_ENABLED` (`true`/`false`)
- `SCOUT_MAX_PAGES_PER_SOURCE`
- `SCOUT_MAX_LINKS_PER_PAGE`
- `SCOUT_MAX_CHARS_PER_PAGE`

### API endpoints

- `POST /grants/scout/run` to trigger a scout run manually.
- `GET /grants/scout/last-report` to fetch the latest run summary.
