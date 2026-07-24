from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    prompt: Mapped[str] = mapped_column(Text)
    selected_model: Mapped[str] = mapped_column(String(100))
    response: Mapped[str] = mapped_column(Text)
    latency_ms: Mapped[float] = mapped_column(Float)
    cost: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(
        back_populates="request",
    )


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("request_logs.id")
    )
    reference_model: Mapped[str] = mapped_column(String(100))
    reference_response: Mapped[str] = mapped_column(Text)
    judge_model: Mapped[str] = mapped_column(String(100))
    winner: Mapped[str] = mapped_column(String(20))
    score: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    request: Mapped["RequestLog"] = relationship(
        back_populates="evaluations"
    )