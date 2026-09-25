import enum
import uuid
from datetime import date, datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    cliente = "cliente"


class RoutineType(str, enum.Enum):
    manual = "manual"
    auto_ia = "auto_ia"


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False, length=50), default=UserRole.cliente, nullable=False)
    position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    routines: Mapped[List["Routine"]] = relationship(back_populates="user")
    metrics: Mapped[List["Metric"]] = relationship(back_populates="user")
    goals: Mapped[List["Goal"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    execution_logs: Mapped[List["ExecutionLog"]] = relationship(back_populates="user")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    objective: Mapped[str] = mapped_column(String(255), nullable=False)
    target_days_per_week: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    available_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user: Mapped["User"] = relationship(back_populates="goals")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    exercises: Mapped[List["Exercise"]] = relationship(back_populates="category")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    category: Mapped["Category"] = relationship(back_populates="exercises")


class Routine(Base):
    __tablename__ = "routines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[RoutineType] = mapped_column(Enum(RoutineType, native_enum=False, length=50), default=RoutineType.manual, nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    effort_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user: Mapped["User"] = relationship(back_populates="routines")
    routine_exercises: Mapped[List["RoutineExercise"]] = relationship(
        back_populates="routine", cascade="all, delete-orphan"
    )
    execution_logs: Mapped[List["ExecutionLog"]] = relationship(back_populates="routine")


class RoutineExercise(Base):
    __tablename__ = "routine_exercises"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    routine_id: Mapped[str] = mapped_column(ForeignKey("routines.id"), nullable=False, index=True)
    exercise_id: Mapped[str] = mapped_column(ForeignKey("exercises.id"), nullable=False, index=True)
    sets: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    effort_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    routine: Mapped["Routine"] = relationship(back_populates="routine_exercises")
    exercise: Mapped["Exercise"] = relationship()


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)

    user: Mapped["User"] = relationship(back_populates="metrics")


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    routine_id: Mapped[str] = mapped_column(ForeignKey("routines.id"), nullable=False, index=True)
    effort_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)

    user: Mapped["User"] = relationship(back_populates="execution_logs")
    routine: Mapped["Routine"] = relationship(back_populates="execution_logs")

    __table_args__ = (
        Index("ix_execution_logs_user_date", "user_id", "executed_at"),
    )