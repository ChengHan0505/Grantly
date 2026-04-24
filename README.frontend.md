# Grantly Frontend (Flutter)

Pixel-focused Flutter implementation of the provided Grantly UI/UX mockups:

- Landing page
- Login page
- Onboarding step 1 (Initialize Copilot)
- Onboarding step 2 (Business Fundamentals)

## Integration with existing project

This frontend is designed to integrate with:

- `../backend` (FastAPI service, default `http://localhost:8000`)
- `../ai_sandbox` (optional AI bridge endpoint, default `http://localhost:8001`)

Runtime URLs are controlled by compile-time defines in `lib/core/app_config.dart`.

## Run backend first

From repo root:

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

## Run frontend

From this `frontend` folder:

```powershell
flutter pub get
flutter run -d chrome --dart-define=BACKEND_BASE_URL=http://localhost:8000 --dart-define=AI_SANDBOX_BASE_URL=http://localhost:8001
```

For Android emulator, replace localhost with `10.0.2.2` for backend URL.

## API layer

`lib/services/grantly_api_service.dart` includes integration methods for:

- backend health check
- user creation
- ranked grants fetch
- optional AI sandbox health ping

You can expand this service to cover the full API from `docs/API_documentation.md`.
