# Grantly Frontend

Next.js frontend for the Grantly Malaysia SME Grant Copilot.

## Getting Started

Install dependencies:

```powershell
npm install
```

Run the development server:

```powershell
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Environment

The frontend reads public runtime configuration from:

- `NEXT_PUBLIC_BACKEND_BASE_URL`
- `NEXT_PUBLIC_AI_SANDBOX_BASE_URL`
- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
- `NEXT_PUBLIC_FIREBASE_APP_ID`

Put these values in `frontend/.env.local` when running the Next.js app from this workspace. The root `.env.local` is not automatically loaded by the frontend package.

## Scripts

- `npm run dev` - start local development
- `npm run build` - create a production build
- `npm run start` - run the production server
- `npm run lint` - run ESLint

## Backend

Start the FastAPI backend from the repo root:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

The frontend defaults to `http://localhost:8000` if `NEXT_PUBLIC_BACKEND_BASE_URL` is not set.
