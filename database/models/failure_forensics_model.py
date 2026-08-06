from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class TraceStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    DEGRADED = "degraded"


class Trace(Base):
    __tablename__ = "traces"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    trace_id: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    status: Mapped[TraceStatus] = mapped_column(
        SqlEnum(TraceStatus),
        nullable=False,
        default=TraceStatus.RUNNING,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    latency_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    total_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    confidence: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    root_cause: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    flagged: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )