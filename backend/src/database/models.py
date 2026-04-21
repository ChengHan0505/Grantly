from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = f"sqlite:///{BASE_DIR / 'grantly.db'}"


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RequirementSource(str, Enum):
    GENERATED = "generated"
    ATTACHED = "attached"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_auth_id: Mapped[str | None] = mapped_column(String(128), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    company_profile: Mapped["SMEProfile | None"] = relationship(back_populates="user", uselist=False)
    documents: Mapped[list["CompanyDocument"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class SMEProfile(Base):
    __tablename__ = "sme_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255))
    industry: Mapped[str | None] = mapped_column(String(120))
    nationality: Mapped[str | None] = mapped_column(String(120))
    annual_revenue: Mapped[float | None] = mapped_column(Float)
    employee_count: Mapped[int | None] = mapped_column(Integer)
    target_grant_amount: Mapped[float | None] = mapped_column(Float)
    business_stage: Mapped[str | None] = mapped_column(String(80))
    summary: Mapped[str | None] = mapped_column(Text)
    questionnaire_answers: Mapped[dict] = mapped_column(JSON, default=dict)
    extracted_data: Mapped[dict] = mapped_column(JSON, default=dict)
    readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user: Mapped[User] = relationship(back_populates="company_profile")


class CompanyDocument(Base):
    __tablename__ = "company_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(100), index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(40), default="uploaded")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped[User] = relationship(back_populates="documents")


class Grant(Base):
    __tablename__ = "grants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    provider_name: Mapped[str] = mapped_column(String(255), index=True)
    source_url: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    amount_min: Mapped[float | None] = mapped_column(Float)
    amount_max: Mapped[float | None] = mapped_column(Float)
    nationality: Mapped[str | None] = mapped_column(String(120))
    industry: Mapped[str | None] = mapped_column(String(120))
    eligibility_notes: Mapped[str | None] = mapped_column(Text)
    application_deadline: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="open")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    requirements: Mapped[list["GrantRequirement"]] = relationship(
        back_populates="grant",
        cascade="all, delete-orphan",
    )


class GrantRequirement(Base):
    __tablename__ = "grant_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    grant_id: Mapped[int] = mapped_column(ForeignKey("grants.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    source_type: Mapped[RequirementSource] = mapped_column(SqlEnum(RequirementSource))
    document_type: Mapped[str | None] = mapped_column(String(100))
    is_required: Mapped[bool] = mapped_column(default=True)

    grant: Mapped[Grant] = relationship(back_populates="requirements")


class SystemState(Base):
    __tablename__ = "system_states"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True, index=True)
    readiness_score: Mapped[float] = mapped_column(Float, default=0.0)
    current_track: Mapped[str] = mapped_column(String(40), default="onboarding")
    evidence_trace: Mapped[dict] = mapped_column(JSON, default=dict)
    last_step: Mapped[str | None] = mapped_column(String(120))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
