# Grantly
The Malaysia SME Grant Copilot

- Frontend: `frontend/` (Next.js)
- Backend: `backend/` (FastAPI)

## Run Locally

Start the backend:

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

Start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000`.
