from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    meta_objetivo: str
    target_days_per_week: Optional[int] = 3
    available_minutes: Optional[int] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    position: Optional[str] = None
    level: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    level: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    meta_objetivo: Optional[str] = None

class GoalResponse(BaseModel):
    id: str
    objetivo: str
    is_active: bool
    alcanzada: bool

    @classmethod
    def from_goal(cls, goal):
        return cls(
            id=goal.id,
            objetivo=goal.objective,
            is_active=goal.is_active,
            alcanzada=not goal.is_active,
        )

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    role: str
    position: Optional[str] = None
    level: Optional[str] = None
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    active_goal: Optional[GoalResponse] = None

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse