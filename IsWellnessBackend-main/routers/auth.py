from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime

from auth import create_access_token, get_current_user, hash_password, verify_password
from database import get_db
from models import User, Goal
from schemas.auth import (
    TokenResponse,
    UserRegister,
    UserResponse,
    GoalResponse,
    UserUpdate,
)
from logger import log_action

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_active_goal(db: Session, user_id: str) -> Goal | None:
    goal = db.query(Goal).filter(
        Goal.user_id == user_id,
        Goal.is_active == True,
    ).first()
    if not goal:
        goal = db.query(Goal).filter(
            Goal.user_id == user_id,
        ).order_by(Goal.created_at.desc()).first()
    return goal


def _build_user_response(user: User, goal: Goal | None) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        position=user.position,
        level=user.level,
        age=user.age,
        height=user.height,
        weight=user.weight,
        active_goal=GoalResponse.from_goal(goal) if goal else None,
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    email = data.email.lower().strip()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya esta registrado",
        )

    user = User(
        email=email,
        password_hash=hash_password(data.password),
        name=data.name,
        position=data.position,
        level=data.level,
        age=data.age,
        height=data.height,
        weight=data.weight,
    )
    db.add(user)
    db.flush()

    goal = Goal(
        user_id=user.id,
        objective=data.meta_objetivo,
        target_days_per_week=data.target_days_per_week or 3,
        available_minutes=data.available_minutes,
        is_active=True,
    )
    db.add(goal)
    db.commit()
    db.refresh(user)

    log_action(user.id, "Registro", f"Meta: {data.meta_objetivo}")

    token = create_access_token(data={"sub": user.id})
    return TokenResponse(access_token=token, user=_build_user_response(user, goal))


@router.post("/login", response_model=TokenResponse)
def login(
    data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = data.username.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    log_action(user.id, "Login")

    token = create_access_token(data={"sub": user.id})
    goal = _get_active_goal(db, user.id)
    return TokenResponse(access_token=token, user=_build_user_response(user, goal))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    goal = _get_active_goal(db, current_user.id)
    return _build_user_response(current_user, goal)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    log_action(current_user.id, "Logout")
    return {"message": "Logout registrado"}


@router.patch("/goal/{goal_id}/achieve")
def achieve_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id,
    ).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meta no encontrada o no pertenece al usuario",
        )

    goal.is_active = False
    goal.updated_at = datetime.now()
    db.commit()

    log_action(current_user.id, "MetaAlcanzada", f"Meta: {goal.objective}")

    return {"message": "Meta marcada como alcanzada exitosamente"}


@router.patch("/update", response_model=UserResponse)
def update_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field in ["name", "position", "level", "age", "height", "weight"]:
        value = getattr(data, field, None)
        if value is not None:
            setattr(current_user, field, value)
    current_user.updated_at = datetime.now()

    if data.meta_objetivo is not None:
        active_goal = db.query(Goal).filter(
            Goal.user_id == current_user.id,
            Goal.is_active == True,
        ).first()

        if active_goal:
            active_goal.objective = data.meta_objetivo
            active_goal.updated_at = datetime.now()
        else:
            db.add(Goal(
                user_id=current_user.id,
                objective=data.meta_objetivo,
                target_days_per_week=3,
                is_active=True,
            ))

    db.commit()
    db.refresh(current_user)

    log_action(current_user.id, "Actualizacion", "Perfil actualizado")

    goal = _get_active_goal(db, current_user.id)
    return _build_user_response(current_user, goal)