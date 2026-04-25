# Grantly
The Malaysia SME Grant Copilot

- Frontend: `frontend/` (Next.js)
- Backend: `backend/` (FastAPI)
- Agents: `backend/ai_sandbox/`

## Run Locally

Start the backend:

```powershell
# Windows
python -m venv venv
venv\Scripts\activte
python install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

Start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Then open `http://localhost:3000`.
