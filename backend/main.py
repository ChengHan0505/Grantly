from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.core.config import settings
from backend.src.database.db import seed_sample_grants
from backend.src.database.models import SessionLocal, init_db
from backend.src.routes import grants_router, health_router, profiles_router


app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def bootstrap() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_sample_grants(db)
    finally:
        db.close()


@app.on_event("startup")
def on_startup() -> None:
    bootstrap()


bootstrap()


app.include_router(health_router)
app.include_router(profiles_router)
app.include_router(grants_router)
