from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class RoutineType(str, Enum):
    manual = "manual"
    auto_ia = "auto_ia"

class ExerciseBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category_id: str

class ExerciseResponse(ExerciseBase):
    pass

class RoutineExerciseResponse(BaseModel):
    id: str
    exercise: ExerciseResponse
    sets: int
    reps: int
    effort_rating: Optional[int] = None

class RoutineResponse(BaseModel):
    id: str
    title: str
    type: RoutineType
    scheduled_date: date
    exercises: List[RoutineExerciseResponse]
    created_at: datetime
    updated_at: datetime
    generado_por: Optional[str] = None

class RoutineGenerateRequest(BaseModel):
    position: Optional[str] = None
    level: Optional[str] = None
    objective: str = Field(..., description="Objetivo de la rutina")
    time_minutes: int = Field(..., ge=5, le=120, description="Tiempo disponible en minutos")
    title: Optional[str] = Field(None, description="Nombre personalizado de la rutina")

class ExerciseManualInput(BaseModel):
    exercise_id: str
    sets: int = Field(3, ge=1, le=20, description="Número de series")
    reps: int = Field(10, ge=1, le=50, description="Número de repeticiones")

class RoutineManualCreate(BaseModel):
    title: str
    scheduled_date: date
    exercises: List[ExerciseManualInput]

class EffortRatingRequest(BaseModel):
    effort_rating: int = Field(..., ge=1, le=5, description="Valoración del 1 al 5")
    routine_exercise_id: Optional[str] = None

    @field_validator("effort_rating")
    @classmethod
    def validate_effort(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("La valoración debe estar entre 1 y 5")
        return v