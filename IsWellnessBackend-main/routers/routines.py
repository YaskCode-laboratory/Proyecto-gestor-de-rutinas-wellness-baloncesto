from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date, datetime

from database import get_db
from models import User, Routine, RoutineExercise, Exercise, Goal, Category, ExecutionLog
from schemas.routine import (
    RoutineResponse,
    RoutineGenerateRequest,
    RoutineManualCreate,
    EffortRatingRequest,
    RoutineExerciseResponse,
    ExerciseResponse,
    ExerciseManualInput,
)
from auth import get_current_user
from logger import log_action
from services.ia_service import generate_routine_from_ia, generate_fallback_routine

router = APIRouter(prefix="/routines", tags=["routines"])


@router.get("/", response_model=List[RoutineResponse])
def get_user_routines(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    routines = db.query(Routine).filter(
        Routine.user_id == current_user.id,
        Routine.is_deleted == False
    ).order_by(Routine.scheduled_date.desc()).all()

    log_action(current_user.id, "Consulta", "Listado de rutinas")
    return [_to_routine_response(r, db) for r in routines]


@router.get("/{routine_id}", response_model=RoutineResponse)
def get_routine(
    routine_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    routine = db.query(Routine).filter(
        Routine.id == routine_id,
        Routine.user_id == current_user.id,
        Routine.is_deleted == False
    ).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    log_action(current_user.id, "Consulta", f"Rutina: {routine.title}")
    return _to_routine_response(routine, db)


@router.post("/generate", response_model=RoutineResponse)
def generate_routine(
    request: RoutineGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    position = request.position or current_user.position or "Base"
    level = request.level or current_user.level or "Intermedio"
    minutes = request.time_minutes
    objective = request.objective
    title_base = request.title or f"Rutina {position} - {date.today().isoformat()}"

    try:
        exercises_data, origen = generate_routine_from_ia(
            position=position,
            level=level,
            minutes=minutes,
            objective=objective,
            age=current_user.age,
            height=current_user.height,
            weight=current_user.weight,
        )
    except Exception as e:
        print(f"Error critico en generacion: {e}")
        exercises_data = generate_fallback_routine(position, level, minutes)
        origen = "fallback"

    sufijo = "(IA)" if origen == "ia" else "(Fallback)"
    title_final = f"{title_base} {sufijo}"

    routine = Routine(
        user_id=current_user.id,
        title=title_final,
        type="auto_ia",
        scheduled_date=date.today(),
    )
    db.add(routine)
    db.flush()

    for ex_data in exercises_data:
        nombre_limpiado = ex_data["name"].strip()
        exercise = None

        exercise = db.query(Exercise).filter(
            func.lower(Exercise.name) == nombre_limpiado.lower()
        ).first()

        if not exercise:
            exercise = db.query(Exercise).filter(
                func.lower(Exercise.name).contains(nombre_limpiado.lower())
            ).first()

        if not exercise:
            category_name = ex_data.get("category", "General").strip()
            if not category_name:
                category_name = "General"

            category = db.query(Category).filter(
                func.lower(Category.name) == category_name.lower()
            ).first()
            if not category:
                category = Category(name=category_name)
                db.add(category)
                db.flush()

            exercise = Exercise(
                name=nombre_limpiado,
                category_id=category.id,
                description=ex_data.get("description", ""),
            )
            db.add(exercise)
            db.flush()

        routine_exercise = RoutineExercise(
            routine_id=routine.id,
            exercise_id=exercise.id,
            sets=ex_data.get("sets", 3),
            reps=ex_data.get("reps", 10),
        )
        db.add(routine_exercise)

    db.commit()
    db.refresh(routine)

    log_action(
        current_user.id,
        "Registro",
        f"Rutina generada: {routine.title} (origen: {origen})"
    )

    return _to_routine_response(routine, db, generado_por=origen)

@router.post("/manual", response_model=RoutineResponse)
def create_manual_routine(
    request: RoutineManualCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exercise_ids = [ex.exercise_id for ex in request.exercises]
    exercises = db.query(Exercise).filter(Exercise.id.in_(exercise_ids)).all()
    if len(exercises) != len(exercise_ids):
        raise HTTPException(status_code=404, detail="Uno o mas ejercicios no existen")

    routine = Routine(
        user_id=current_user.id,
        title=request.title,
        type="manual",
        scheduled_date=request.scheduled_date,
    )
    db.add(routine)
    db.flush()

    for ex_data in request.exercises:
        exercise = next((e for e in exercises if e.id == ex_data.exercise_id), None)
        if exercise:
            routine_exercise = RoutineExercise(
                routine_id=routine.id,
                exercise_id=exercise.id,
                sets=ex_data.sets,
                reps=ex_data.reps,
            )
            db.add(routine_exercise)

    db.commit()
    db.refresh(routine)

    log_action(current_user.id, "Registro", f"Rutina manual: {routine.title}")
    return _to_routine_response(routine, db, generado_por="manual")


@router.patch("/{routine_id}/execute")
def execute_routine(
    routine_id: str,
    effort: EffortRatingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    routine = db.query(Routine).filter(
        Routine.id == routine_id,
        Routine.user_id == current_user.id,
        Routine.is_deleted == False
    ).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    routine.effort_rating = effort.effort_rating
    routine.updated_at = datetime.now()

    for re in routine.routine_exercises:
        if not re.is_deleted:
            re.effort_rating = effort.effort_rating
            re.updated_at = datetime.now()

    db.commit()

    execution_log = ExecutionLog(
        user_id=current_user.id,
        routine_id=routine.id,
        effort_rating=effort.effort_rating,
    )
    db.add(execution_log)
    db.commit()

    log_action(
        current_user.id,
        "Ejecucion",
        f"Rutina: {routine.title}, Esfuerzo: {effort.effort_rating}"
    )

    return {"message": "Rutina ejecutada y valorada exitosamente"}


@router.delete("/{routine_id}")
def delete_routine(
    routine_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    routine = db.query(Routine).filter(
        Routine.id == routine_id,
        Routine.user_id == current_user.id,
        Routine.is_deleted == False
    ).first()
    if not routine:
        raise HTTPException(status_code=404, detail="Rutina no encontrada")

    routine.is_deleted = True
    routine.updated_at = datetime.now()
    db.commit()

    log_action(current_user.id, "Eliminacion", f"Rutina: {routine.title}")
    return {"message": "Rutina eliminada exitosamente"}


def _to_routine_response(routine: Routine, db: Session, generado_por: str = None) -> RoutineResponse:
    exercises = []
    for re in routine.routine_exercises:
        if re.is_deleted:
            continue
        exercises.append(
            RoutineExerciseResponse(
                id=re.id,
                exercise=ExerciseResponse(
                    id=re.exercise.id,
                    name=re.exercise.name,
                    description=re.exercise.description,
                    category_id=re.exercise.category_id,
                ),
                sets=re.sets,
                reps=re.reps,
                effort_rating=re.effort_rating,
            )
        )

    return RoutineResponse(
        id=routine.id,
        title=routine.title,
        type=routine.type,
        scheduled_date=routine.scheduled_date,
        exercises=exercises,
        created_at=routine.created_at,
        updated_at=routine.updated_at,
        generado_por=generado_por,
    )