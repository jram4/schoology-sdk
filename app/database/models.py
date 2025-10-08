from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Text, Enum
from datetime import datetime, timezone
from app.database.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Assignment(Base):
    __tablename__ = "assignments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, index=True)
    course_name: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(400))
    due_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    url: Mapped[str | None] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(32), default="open")
    last_seen_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(400))
    start_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(255))

class Update(Base):
    __tablename__ = "updates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author: Mapped[str] = mapped_column(String(255))
    content_html_sanitized: Mapped[str] = mapped_column(Text)
    posted_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    source: Mapped[str] = mapped_column(String(255))

class Grade(Base):
    __tablename__ = "grades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, index=True)
    course_name: Mapped[str] = mapped_column(String(255))
    assignment_id: Mapped[int] = mapped_column(Integer, index=True)
    assignment_title: Mapped[str] = mapped_column(String(400))
    score_raw: Mapped[str | None] = mapped_column(String(64))
    score_pct: Mapped[float | None] = mapped_column()
    posted_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

class PlannerTask(Base):
    __tablename__ = "planner_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(400))
    due_at_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    origin: Mapped[str] = mapped_column(String(16), default="personal")  # 'schoology'|'personal'
    schoology_assignment_id: Mapped[int | None] = mapped_column(Integer, index=True)
    column: Mapped[str] = mapped_column(String(16), default="todo")  # 'todo','in_progress','done'
    priority: Mapped[int] = mapped_column(Integer, default=0)
